# app/crud/crud.py
from sqlalchemy.orm import Session
from .. import models, schemas

def create_task(db: Session, task: schemas.TaskCreate):
    db_task = models.Task(
        target_name=task.target_name,
        target_url=task.target_url  # 新增：保存目标URL
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def create_comment(db: Session, comment: schemas.CommentCreate, task_id: int):
    # Pydantic V2 使用 model_dump() 而不是 dict()
    db_comment = models.Comment(**comment.model_dump(), task_id=task_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

def get_tasks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Task).offset(skip).limit(limit).all()

def update_task_sentiment(db: Session, task_id: int, sentiment_analysis: str):
    """更新任务的情绪分析结果"""
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task:
        db_task.sentiment_analysis = sentiment_analysis
        db.commit()
        db.refresh(db_task)
    return db_task