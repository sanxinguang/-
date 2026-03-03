# app/models/models.py
from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from ..db.session import Base

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    target_name = Column(String, index=True)
    target_url = Column(String, nullable=False)
    sentiment_analysis = Column(String, nullable=True)  # 新增：情绪分析结果
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    comments = relationship("Comment", back_populates="task")

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    author = Column(String)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    task = relationship("Task", back_populates="comments")