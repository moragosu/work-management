from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
import uuid
import data_store

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


class QuestionUpdate(BaseModel):
    question: str


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
def create_question(body: QuestionCreate):
    questions, answers = _load()
    new_q = {
        "id": f"Q{str(uuid.uuid4())[:8].upper()}",
        "task_id": body.task_id,
        "week": body.week,
        "question": body.question,
        "created_at": date.today().isoformat(),
    }
    questions.append(new_q)
    _save(questions, answers)
    return {**new_q, "answers": []}


@router.put("/questions/{question_id}")
def update_question(question_id: str, body: QuestionUpdate):
    questions, answers = _load()
    for q in questions:
        if q["id"] == question_id:
            q["question"] = body.question
            _save(questions, answers)
            q_answers = [a for a in answers if a["question_id"] == question_id]
            return {**q, "answers": q_answers}
    raise HTTPException(status_code=404, detail="Question not found")


@router.delete("/questions/{question_id}")
def delete_question(question_id: str):
    questions, answers = _load()
    questions = [q for q in questions if q["id"] != question_id]
    answers = [a for a in answers if a["question_id"] != question_id]
    _save(questions, answers)
    return {"deleted": question_id}


@router.post("/answers", status_code=201)
def create_answer(body: AnswerCreate):
    questions, answers = _load()
    if not any(q["id"] == body.question_id for q in questions):
        raise HTTPException(status_code=404, detail="Question not found")
    new_a = {
        "id": f"A{str(uuid.uuid4())[:8].upper()}",
        "question_id": body.question_id,
        "answer": body.answer,
        "answer_by": body.answer_by,
        "images": body.images,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    answers.append(new_a)
    _save(questions, answers)
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
