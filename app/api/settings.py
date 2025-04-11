from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import get_current_active_user
from app.models.models import Users, SystemSettings, ProblemType, SolutionType, WorkOrders
from app.schemas.settings import SystemSettingsUpdate
from typing import List

router = APIRouter()

@router.get("/system")
async def get_system_settings(
    current_user: Users = Depends(get_current_active_user)
):
    """获取系统设置"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    settings = await SystemSettings.get_settings()
    return settings

@router.put("/system")
async def update_system_settings(
    settings: SystemSettingsUpdate,
    current_user: Users = Depends(get_current_active_user)
):
    """更新系统设置"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    await SystemSettings.update_settings(settings.archive_hours)
    return {"message": "更新成功"}

@router.get("/problem-types")
async def get_problem_types(
    current_user: Users = Depends(get_current_active_user)
):
    """获取所有问题类型"""
    types = await ProblemType.all()
    return [{"name": t.name} for t in types]

@router.post("/problem-types")
async def create_problem_type(
    type_data: dict,
    current_user: Users = Depends(get_current_active_user)
):
    """创建问题类型"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    name = type_data.get("name")
    if not name:
        raise HTTPException(status_code=400, detail="类型名称不能为空")
    
    # 检查名称是否已存在
    exists = await ProblemType.get_or_none(name=name)
    if exists:
        raise HTTPException(status_code=400, detail="该类型名称已存在")
    
    # 创建新类型
    await ProblemType.create(name=name)
    return {"message": "创建成功"}

@router.delete("/problem-types/{name}")
async def delete_problem_type(
    name: str,
    current_user: Users = Depends(get_current_active_user)
):
    """删除问题类型"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    # 检查类型是否存在
    problem_type = await ProblemType.get_or_none(name=name)
    if not problem_type:
        raise HTTPException(status_code=404, detail="问题类型不存在")
    
    # 删除类型
    await problem_type.delete()
    return {"message": "删除成功"}

@router.get("/solution-types")
async def get_solution_types(
    current_user: Users = Depends(get_current_active_user)
):
    """获取所有解决方案类型"""
    types = await SolutionType.all()
    return [{"name": t.name} for t in types]

@router.post("/solution-types")
async def create_solution_type(
    type_data: dict,
    current_user: Users = Depends(get_current_active_user)
):
    """创建解决方案类型"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    name = type_data.get("name")
    if not name:
        raise HTTPException(status_code=400, detail="类型名称不能为空")
    
    # 检查名称是否已存在
    exists = await SolutionType.get_or_none(name=name)
    if exists:
        raise HTTPException(status_code=400, detail="该类型名称已存在")
    
    # 创建新类型
    await SolutionType.create(name=name)
    return {"message": "创建成功"}

@router.delete("/solution-types/{name}")
async def delete_solution_type(
    name: str,
    current_user: Users = Depends(get_current_active_user)
):
    """删除解决方案类型"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    # 检查类型是否存在
    solution_type = await SolutionType.get_or_none(name=name)
    if not solution_type:
        raise HTTPException(status_code=404, detail="解决方案类型不存在")
    
    # 删除类型
    await solution_type.delete()
    return {"message": "删除成功"} 