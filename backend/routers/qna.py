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


class ReplyCreate(BaseModel):
    reply: str
    reply_by: str


class ReplyUpdate(BaseModel):
    reply: str


@router.get("/questions")
def list_questions(week: Optional[str] = Query(None), task_id: Optional[str] = Query(None)):
    questions, answers = _load()
    if week:
        questions = [q for q in questions if q.get("week") == week]
    if task_id:
        questions = [q for q in questions if q.get("task_id") == task_id]
    # 대댓글 로드
    with data_store.get_conn() as conn:
        all_replies = [dict(r) for r in conn.execute("SELECT * FROM answer_replies ORDER BY created_at").fetchall()]
    result = []
    for q in questions:
        q_answers = []
        for a in answers:
            if a["question_id"] == q["id"]:
                a_dict = dict(a)
                a_dict["replies"] = [r for r in all_replies if r["answer_id"] == a["id"]]
                q_answers.append(a_dict)
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
            f"/progress?week={body.week}&focusQuestion={new_q['id']}",
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
    if not user.get("is_admin") and target.get("created_by") != user["username"]:
        raise HTTPException(status_code=403, detail="본인이 작성한 질문만 삭제할 수 있습니다")
    questions = [q for q in questions if q["id"] != question_id]
    answers = [a for a in answers if a["question_id"] != question_id]
    _save(questions, answers)
    return {"deleted": question_id}


@router.post("/answers", status_code=201)
def create_answer(body: AnswerCreate, user: dict = Depends(get_current_user)):
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
        "created_by": user["username"],
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
            f"/progress?week={target_q.get('week', '')}&focusQuestion={body.question_id}",
        )
    return new_a


@router.put("/answers/{answer_id}")
def update_answer(answer_id: str, body: AnswerUpdate, user: dict = Depends(get_current_user)):
    questions, answers = _load()
    for a in answers:
        if a["id"] == answer_id:
            if not user.get("is_admin") and a.get("created_by") != user["username"] and a.get("answer_by") != user.get("name"):
                raise HTTPException(status_code=403, detail="본인이 작성한 답변만 수정할 수 있습니다")
            a["answer"] = body.answer
            a["answer_by"] = body.answer_by
            a["images"] = body.images
            a["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            _save(questions, answers)
            return a
    raise HTTPException(status_code=404, detail="Answer not found")


@router.delete("/answers/{answer_id}")
def delete_answer(answer_id: str, user: dict = Depends(get_current_user)):
    questions, answers = _load()
    target_a = next((a for a in answers if a["id"] == answer_id), None)
    if not target_a:
        raise HTTPException(status_code=404, detail="Answer not found")
    if not user.get("is_admin") and target_a.get("created_by") != user["username"] and target_a.get("answer_by") != user.get("name"):
        raise HTTPException(status_code=403, detail="본인이 작성한 답변만 삭제할 수 있습니다")
    answers = [a for a in answers if a["id"] != answer_id]
    _save(questions, answers)

    # 답변 삭제 후 해당 질문에 남은 답변이 없으면 대상자에게 알림 재발송
    if target_a:
        qid = target_a["question_id"]
        remaining = [a for a in answers if a["question_id"] == qid]
        if not remaining:
            target_q = next((q for q in questions if q["id"] == qid), None)
            if target_q:
                week = target_q.get("week", "")
                link = f"/progress?week={week}&focusQuestion={qid}"
                preview = target_q.get("question", "")[:40].replace("\n", " ")
                questioner = target_q.get("questioner", "질문자")
                with data_store.get_conn() as conn:
                    for target_name in target_q.get("targets", []):
                        recipient = data_store.get_username_for_notification(target_name)
                        if not recipient:
                            continue
                        # 동일 link의 question_tagged 알림이 이미 있으면 재발송 안 함
                        exists = conn.execute(
                            "SELECT 1 FROM notifications WHERE recipient=? AND type='question_tagged' AND link=?",
                            (recipient, link)
                        ).fetchone()
                        if not exists:
                            data_store.insert_notification(
                                recipient, "question_tagged",
                                "답변이 삭제되어 질문이 미답변 상태입니다",
                                f"{questioner}: {preview}",
                                link,
                            )

    return {"deleted": answer_id}


# ── 대댓글 ────────────────────────────────────────────────────────────────────

@router.post("/answers/{answer_id}/replies", status_code=201)
def create_reply(answer_id: str, body: ReplyCreate, user: dict = Depends(get_current_user)):
    with data_store.get_conn() as conn:
        new_r = {
            "id": short_uuid("R"),
            "answer_id": answer_id,
            "reply": body.reply,
            "reply_by": body.reply_by,
            "created_by": user["username"],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "updated_at": None,
        }
        conn.execute(
            "INSERT INTO answer_replies (id,answer_id,reply,reply_by,created_by,created_at) VALUES (?,?,?,?,?,?)",
            (new_r["id"], answer_id, body.reply, body.reply_by, user["username"], new_r["created_at"]),
        )
    return new_r


@router.put("/answers/{answer_id}/replies/{reply_id}")
def update_reply(answer_id: str, reply_id: str, body: ReplyUpdate, user: dict = Depends(get_current_user)):
    with data_store.get_conn() as conn:
        row = conn.execute("SELECT * FROM answer_replies WHERE id=?", (reply_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Reply not found")
        if not user.get("is_admin") and row["created_by"] != user["username"]:
            raise HTTPException(status_code=403, detail="본인이 작성한 답글만 수정할 수 있습니다")
        updated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
        conn.execute(
            "UPDATE answer_replies SET reply=?, updated_at=? WHERE id=?",
            (body.reply, updated_at, reply_id),
        )
    return {**dict(row), "reply": body.reply, "updated_at": updated_at}


@router.delete("/answers/{answer_id}/replies/{reply_id}")
def delete_reply(answer_id: str, reply_id: str, user: dict = Depends(get_current_user)):
    with data_store.get_conn() as conn:
        row = conn.execute("SELECT created_by FROM answer_replies WHERE id=?", (reply_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Reply not found")
        if not user.get("is_admin") and row["created_by"] != user["username"]:
            raise HTTPException(status_code=403, detail="본인이 작성한 답글만 삭제할 수 있습니다")
        conn.execute("DELETE FROM answer_replies WHERE id=?", (reply_id,))
    return {"deleted": reply_id}
