#!/usr/bin/env python3
"""
数据库初始化脚本
用于创建数据库表结构
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.db.session import Base, engine, SQLALCHEMY_DATABASE_URL
from app.models.models import Task, Comment

def create_database_if_not_exists():
    """如果数据库不存在则创建"""
    try:
        # 尝试连接到数据库
        test_engine = create_engine(SQLALCHEMY_DATABASE_URL.replace('/comment_db', '/postgres'))
        with test_engine.connect() as conn:
            # 检查数据库是否存在
            result = conn.execute(text("SELECT 1 FROM pg_database WHERE datname = 'comment_db'"))
            if not result.fetchone():
                print("数据库 comment_db 不存在，正在创建...")
                conn.execute(text("COMMIT"))  # 结束当前事务
                conn.execute(text("CREATE DATABASE comment_db"))
                print("数据库 comment_db 创建成功！")
            else:
                print("数据库 comment_db 已存在")
    except Exception as e:
        print(f"检查/创建数据库时出错: {e}")
        return False
    return True

def create_tables():
    """创建所有表"""
    try:
        print("正在创建数据库表...")
        Base.metadata.create_all(bind=engine)
        print("数据库表创建成功！")
        return True
    except Exception as e:
        print(f"创建表时出错: {e}")
        return False

def main():
    print("开始初始化数据库...")
    
    # 1. 创建数据库（如果不存在）
    if not create_database_if_not_exists():
        print("数据库初始化失败")
        return False
    
    # 2. 创建表
    if not create_tables():
        print("表创建失败")
        return False
    
    print("数据库初始化完成！")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
