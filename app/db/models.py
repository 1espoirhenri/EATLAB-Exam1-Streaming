# app/db/models.py
from sqlalchemy import Column, String, Integer, JSON, DateTime
from datetime import datetime
from .base import Base

class Feedback(Base):
    __tablename__ = "feedback"
    id          = Column(String, primary_key=True, index=True)
    frame_hash  = Column(String, index=True)
    bbox        = Column(JSON)           # [x1,y1,x2,y2]
    pred_label  = Column(String)
    user_label  = Column(String)
    accepted    = Column(Integer)        # 1 (đúng) / 0 (sai / sửa)
    created_at  = Column(DateTime, default=datetime.utcnow)
