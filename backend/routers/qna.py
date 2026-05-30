from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
import data_store
from utils.id_generator import short_uuid
from dependencies import get_current_user, require_admin

router = APIRouter()


def _load():
    data = data_store.load("qna.json")
    return data.get("questions", []), data.get("answers", [])


def _save(questions, answers):
    data_store.save("qna.json", {"questions": questions, "answers": answers})


class QuestionCreate(BaseModel):
    task_id: str
    week: str
    question: str
    targets: list = []
    questioner: Optional[str] = None


class QuestionUpdate(BaseModel):
    question: str
    targets: Optional[list] = None
    questioner: Optional[str] = None


class AnswerCreate(BaseModel):
    question_id: str
    answer: str
    answer_by: str
    images: list = []


class AnswerUpdate(BaseModel):
    answer: str
    answer_by: str
    images: list = []


@router.get("/questions")
def list_questions(week: Optional[str] = Query(None), task_id: Optional[str] = Query(None)):
    questions, answers = _load()
    if week:
        questions = [q for q in questions if q.get("week") == week]
    if task_id:
        questions = [q for q in questions if q.get("task_id") == task_id]
    result = []
    for q in questions:
        q_answers = [a for a in answers if a["question_id"] == q["id"]]
        result.append({**q, "answers": q_answers})
    return result


@router.post("/questions", status_code=201)
def create_question(body: QuestionCreate, user: dict = Depends(get_current_user)):
    questions, answers = _load()
    new_q = {
        "id": short_uuid("Q"),
        "task_id": body.task_id,
        "week": body.week,
        "question": body.question,
        "targets": body.targets,
        "questioner": body.questioner or "",
        "created_by": user["username"],
        "created_at": date.today().isoformat(),
    }
    questions.append(new_q)
    _save(questions, answers)
    # 알림: 질문 대상자에게
    preview = body.question[:40].replace('\n', ' ')
    for target_name in body.targets:
        recipient = data_store.get_username_for_notification(target_name)
        data_store.insert_notification(
            recipient, "question_tagged",
            "새 질문이 등록되었습니다",
            f"{body.questioner or '질문자'}: {preview}",
            "/progress",
        )
    return {**new_q, "answers": []}


@router.put("/questions/{question_id}")
def update_question(question_id: str, body: QuestionUpdate):
    questions, answers = _load()
    for q in questions:
        if q["id"] == question_id:
            q["question"] = body.question
            if body.targets is not None:
                q["targets"] = body.targets
            if body.questioner is not None:
                q["questioner"] = body.questioner
            _save(questions, answers)
            q_answers = [a for a in answers if a["question_id"] == question_id]
            return {**q, "answers": q_answers}
    raise HTTPException(status_code=404, detail="Question not found")


@router.delete("/questions/{question_id}")
def delete_question(question_id: str, user: dict = Depends(get_current_user)):
    questions, answers = _load()
    target = next((q for q in questions if q["id"] == question_id), None)
    if not target:
        raise HTTPException(status_code=404, detail="Question not found")
    if user["role"] != "admin" and target.get("created_by") != user["username"]:
        raise HTTPException(status_code=403, detail="본인이 작성한 질문만 삭제할 수 있습니다")
    questions = [q for q in questions if q["id"] != question_id]
    answers = [a for a in answers if a["question_id"] != question_id]
    _save(questions, answers)
    return {"deleted": question_id}


@router.post("/answers", status_code=201)
def create_answer(body: AnswerCreate):
    questions, answers = _load()
    target_q = next((q for q in questions if q["id"] == body.question_id), None)
    if not target_q:
        raise HTTPException(status_code=404, detail="Question not found")
    new_a = {
        "id": short_uuid("A"),
        "question_id": body.question_id,
        "answer": body.answer,
        "answer_by": body.answer_by,
        "images": body.images,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    answers.append(new_a)
    _save(questions, answers)
    # 알림: 질문자에게
    questioner_name = target_q.get("questioner", "")
    recipient = data_store.get_username_for_notification(questioner_name)
    if recipient and recipient != data_store.get_username_for_notification(body.answer_by):
        data_store.insert_notification(
            recipient, "answer_received",
            "답변이 달렸습니다",
            f"{body.answer_by}님이 답변을 등록했습니다",
            "/progress",
        )
    return new_a


@router.put("/answers/{answer_id}")
def update_answer(answer_id: str, body: AnswerUpdate):
    questions, answers = _load()
    for a in answers:
        if a["id"] == answer_id:
            a["answer"] = body.answer
            a["answer_by"] = body.answer_by
            a["images"] = body.images
            a["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            _save(questions, answers)
            return a
    raise HTTPException(status_code=404, detail="Answer not found")


@router.delete("/answers/{answer_id}")
def delete_answer(answer_id: str):
    questions, answers = _load()
    answers = [a for a in answers if a["id"] != answer_id]
    _save(questions, answers)
    return {"deleted": answer_id}
