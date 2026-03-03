# 网易云音乐评论数据情感分析系统

基于 FastAPI + Celery + DeepSeek LLM 的评论情感分析系统。通过抓取网易云音乐评论数据，利用大语言模型进行情感分析，输出情绪分布、关键情绪词和话题主题等分析结果。

## 技术栈

- **Web 框架**：FastAPI
- **任务队列**：Celery + Redis
- **数据库**：PostgreSQL + SQLAlchemy
- **数据校验**：Pydantic V2
- **AI 分析**：DeepSeek API

## 系统架构

```
用户请求 → FastAPI API → 创建任务入库
                          ↓
                   Celery 异步任务
                          ↓
              requests 抓取网易云音乐评论
                          ↓
                  评论保存到 PostgreSQL
                          ↓
              DeepSeek API 情感分析
                          ↓
                分析结果保存到数据库
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env`，并填入你自己的配置：

```bash
cp .env.example .env
```

### 3. 启动 Redis

确保本地 Redis 服务已启动（Celery 需要 Redis 作为消息队列）：

```bash
redis-server
```

### 4. 初始化数据库

```bash
python init_db.py
```

### 5. 启动 Celery Worker

```bash
celery -A app.tasks.worker.celery_app worker --loglevel=info
```

### 6. 启动 API 服务

```bash
uvicorn main:app --reload
```

启动后访问 http://localhost:8000/docs 查看 API 文档。

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/tasks/` | 创建爬取分析任务 |
| GET | `/api/v1/tasks/` | 查询任务列表及分析结果 |
| GET | `/health` | 健康检查 |

### 创建任务示例

```json
POST /api/v1/tasks/
{
    "target_name": "某首歌曲",
    "target_url": "https://music.163.com/api/v1/resource/comments/R_SO_4_歌曲ID?limit=20"
}
```

## 项目结构

```
├── main.py                 # FastAPI 应用入口
├── init_db.py              # 数据库初始化脚本
├── requirements.txt        # Python 依赖
├── .env.example            # 环境变量模板
└── app/
    ├── api/
    │   └── endpoints.py    # API 路由端点
    ├── crud/
    │   └── crud.py         # 数据库 CRUD 操作
    ├── db/
    │   └── session.py      # 数据库连接配置
    ├── models/
    │   └── models.py       # SQLAlchemy 数据模型
    ├── schemas/
    │   └── schemas.py      # Pydantic 数据校验
    ├── services/
    │   └── llm_service.py  # DeepSeek LLM 情感分析
    └── tasks/
        └── worker.py       # Celery 异步任务
```

