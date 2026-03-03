# app/schemas/schemas.py
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

class CommentBase(BaseModel):
    content: str
    author: Optional[str] = None

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: int
    task_id: int
    class Config:
        from_attributes = True  # Pydantic V2 语法

class TaskBase(BaseModel):
    target_name: str
    target_url: str

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    id: int
    created_at: datetime
    sentiment_analysis: Optional[str] = None  # 新增：情绪分析结果
    comments: List[Comment] = []
    class Config:
        from_attributes = True  # Pydantic V2 语法