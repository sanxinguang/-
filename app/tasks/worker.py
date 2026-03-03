# app/tasks/worker.py
from celery import Celery
import requests
from app.db.session import SessionLocal
from app.crud.crud import create_comment, update_task_sentiment
from app.schemas.schemas import CommentCreate
from app.models import models
from app.services.llm_service import llm_service

# 配置 Celery，添加 result backend
celery_app = Celery('worker', 
                   broker='redis://localhost:6379/0',
                   result_backend='redis://localhost:6379/0')

@celery_app.task
def crawl_comments_task(task_id: int):
    """
    爬取评论任务
    1. 从数据库获取任务的 target_url
    2. 爬取评论数据
    3. 保存评论到数据库
    4. 使用 LLM 分析评论情绪
    5. 保存分析结果到任务表
    """
    try:
        # 获取数据库会话
        db = SessionLocal()
        
        # 从数据库获取任务信息，包括 target_url
        task = db.query(models.Task).filter(models.Task.id == task_id).first()
        if not task:
            db.close()
            return f"Task {task_id} failed: Task not found in database"
        
        # 使用任务中的 target_url 进行爬取
        url = task.target_url
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        # 解析并存储热门评论
        comments_data = data.get('hotComments', [])
        
        # 保存评论到数据库
        saved_comments = []
        for item in comments_data:
            comment_data = CommentCreate(
                content=item.get('content', ''),
                author=item.get('user', {}).get('nickname', 'Unknown')
            )
            db_comment = create_comment(db=db, comment=comment_data, task_id=task_id)
            saved_comments.append({
                'author': db_comment.author,
                'content': db_comment.content
            })
        
        # 使用 LLM 分析评论情绪
        print(f"开始分析任务 {task_id} 的评论情绪...")
        sentiment_result = llm_service.analyze_comments_sentiment(saved_comments)
        
        # 保存分析结果到任务表
        update_task_sentiment(db=db, task_id=task_id, sentiment_analysis=sentiment_result)
        print(f"任务 {task_id} 情绪分析完成")
        
        db.close()
        return f"Task {task_id}: Crawled {len(comments_data)} comments from {url}, sentiment analyzed"
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Task {task_id} failed: {str(e)}"