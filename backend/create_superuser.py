#!/usr/bin/env python3
"""
创建超级用户脚本
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models import Base
from app.models.user import User
from app.core.security import get_password_hash

def create_superuser():
    """创建超级用户"""
    # 创建数据库表
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    
    try:
        # 检查是否已存在超级用户
        existing_user = db.query(User).filter(User.username == "admin").first()
        if existing_user:
            print("超级用户 'admin' 已存在")
            return
        
        # 创建超级用户
        hashed_password = get_password_hash("admin123")
        superuser = User(
            username="admin",
            email="admin@example.com",
            hashed_password=hashed_password,
            full_name="系统管理员",
            is_active=True,
            is_superuser=True
        )
        
        db.add(superuser)
        db.commit()
        db.refresh(superuser)
        
        print("超级用户创建成功！")
        print("用户名: admin")
        print("密码: admin123")
        print("邮箱: admin@example.com")
        
    except Exception as e:
        print(f"创建超级用户失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_superuser()
