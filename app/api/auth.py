from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.config import settings
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.models import Users, User_Pydantic
from app.schemas.auth import Token, UserCreate
from app.api.deps import get_current_admin_user, get_current_active_user
from typing import List

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """用户登录"""
    user = await Users.get_or_none(username=form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "is_admin": user.is_admin
        }
    }

@router.get("/users", response_model=List[User_Pydantic])
async def get_users(current_user: Users = Depends(get_current_active_user)):
    """获取用户列表"""
    users = await Users.filter(is_active=True).all()
    return users

@router.post("/users", response_model=User_Pydantic)
async def create_user(user_in: UserCreate, current_user: Users = Depends(get_current_admin_user)):
    """创建用户（仅管理员）"""
    user = await Users.get_or_none(username=user_in.username)
    if user:
        raise HTTPException(
            status_code=400,
            detail="用户名已存在"
        )
    user = await Users.create(
        username=user_in.username,
        password_hash=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        is_admin=user_in.is_admin
    )
    return user

@router.put("/users/{user_id}", response_model=User_Pydantic)
async def update_user(
    user_id: int,
    user_in: UserCreate,
    current_user: Users = Depends(get_current_admin_user)
):
    """更新用户信息（仅管理员）"""
    user = await Users.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 检查用户名是否已被其他用户使用
    if user_in.username != user.username:
        existing_user = await Users.get_or_none(username=user_in.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="用户名已存在")
    
    user.username = user_in.username
    user.full_name = user_in.full_name
    user.is_admin = user_in.is_admin
    if user_in.password:
        user.password_hash = get_password_hash(user_in.password)
    await user.save()
    return user

@router.delete("/users/{user_id}")
async def delete_user(user_id: int, current_user: Users = Depends(get_current_admin_user)):
    """删除用户（仅管理员）"""
    user = await Users.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 不允许删除自己
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="不能删除当前登录用户")
    
    user.is_active = False
    await user.save()
    return {"message": "用户已删除"}

@router.put("/users/{user_id}/password")
async def change_password(
    user_id: int,
    password_data: dict,
    current_user: Users = Depends(get_current_active_user)
):
    """修改用户密码"""
    # 只能修改自己的密码，除非是管理员
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="无权修改其他用户的密码")
    
    user = await Users.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 验证原密码
    if not verify_password(password_data["old_password"], user.password_hash):
        raise HTTPException(status_code=400, detail="原密码错误")
    
    # 更新密码
    user.password_hash = get_password_hash(password_data["new_password"])
    await user.save()
    
    return {"message": "密码修改成功"} 