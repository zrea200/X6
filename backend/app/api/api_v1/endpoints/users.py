from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user, get_current_active_superuser
from app.schemas.user import User, UserUpdate
from app.services.user_service import UserService
from app.models.user import User as UserModel

router = APIRouter()

@router.get("/me", response_model=User)
async def read_user_me(
    current_user: UserModel = Depends(get_current_user)
):
    """获取当前用户信息"""
    return current_user

@router.put("/me", response_model=User)
async def update_user_me(
    user_update: UserUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新当前用户信息"""
    user_service = UserService(db)
    updated_user = user_service.update_user(current_user.id, user_update)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return updated_user

@router.get("/", response_model=List[User])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(get_current_active_superuser),
    db: Session = Depends(get_db)
):
    """获取用户列表（仅超级用户）"""
    user_service = UserService(db)
    users = user_service.get_users(skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=User)
async def read_user(
    user_id: int,
    current_user: UserModel = Depends(get_current_active_superuser),
    db: Session = Depends(get_db)
):
    """获取指定用户信息（仅超级用户）"""
    user_service = UserService(db)
    user = user_service.get_user(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user
