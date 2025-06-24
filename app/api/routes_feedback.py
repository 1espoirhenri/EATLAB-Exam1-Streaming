# app/api/routes_feedback.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..db import models, base
import uuid, datetime

router = APIRouter()

class FeedbackIn(BaseModel):
    frame_id: str
    bbox: list       # [x1,y1,x2,y2]
    pred_label: str
    user_label: str | None = None
    accepted: bool

@router.post("/feedback")
def post_feedback(data: FeedbackIn, db: Session = Depends(base.get_db)):
    fb = models.Feedback(
        id=str(uuid.uuid4()),
        frame_hash=data.frame_id,
        bbox=data.bbox,
        pred_label=data.pred_label,
        user_label=data.user_label or "",
        accepted=1 if data.accepted else 0,
        created_at=datetime.datetime.utcnow()
    )
    db.add(fb); db.commit()
    return {"status": "ok"}
