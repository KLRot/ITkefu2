from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Header
from app.api.deps import get_current_active_user
from app.models.models import Users, WorkOrders, SystemSettings, ProblemType, SolutionType
from app.schemas.work_order import (
    WorkOrderCreate,
    WorkOrderUpdate,
    WorkOrderAssign,
    WorkOrderInDB
)
from app.services.work_order import WorkOrderService
from datetime import datetime, timedelta
from tortoise.expressions import Q
from tortoise.transactions import in_transaction

router = APIRouter()

API_TOKEN = "kinglong"

async def verify_token(authorization: Optional[str] = Header(None)):
    """验证API Token"""
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="缺少认证信息",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != 'bearer':
            raise HTTPException(
                status_code=401,
                detail="认证方案无效，请使用Bearer认证",
                headers={"WWW-Authenticate": "Bearer"}
            )
        if token != API_TOKEN:
            raise HTTPException(
                status_code=401,
                detail="Token无效",
                headers={"WWW-Authenticate": "Bearer"}
            )
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="认证格式无效",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return authorization

async def generate_order_no():
    today = datetime.now()
    date_str = today.strftime("%Y%m%d")
    base_no = f"SZIT-{date_str}-"
    
    # 获取今天的最后一个工单编号
    last_order = await WorkOrders.filter(
        order_no__startswith=f"SZIT-{date_str}"
    ).order_by("-order_no").first()
    
    if last_order:
        last_number = int(last_order.order_no.split("-")[-1])
        new_number = str(last_number + 1).zfill(3)
    else:
        new_number = "001"
    
    return f"{base_no}{new_number}"

@router.post("", response_model=WorkOrderInDB)
@router.post("/", response_model=WorkOrderInDB)
async def create_work_order(
    work_order: WorkOrderCreate,
    token: str = Depends(verify_token)
):
    """创建工单 - 仅支持API Token认证"""
    # 生成工单编号
    order_no = await generate_order_no()
    
    try:
        new_order = await WorkOrders.create(
            order_no=order_no,
            reporter_name=work_order.reporter_name,
            contact_phone=work_order.contact_phone,
            location=work_order.location,
            problem_desc=work_order.problem_desc,
            status=0,  # 新建状态
            assigned_to=None,  # 明确设置为None
            problem_type=None,
            processing_desc=None,
            solution_type=None
        )
        
        # 重新获取工单以包含所有关联数据
        created_order = await WorkOrders.get(id=new_order.id).prefetch_related("assigned_to")
        return created_order
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"创建工单失败: {str(e)}"
        )

@router.put("/{work_order_id}/assign", response_model=WorkOrderInDB)
async def assign_work_order(
    work_order_id: int,
    current_user: Users = Depends(get_current_active_user)
):
    """分配工单"""
    try:
        async with in_transaction() as connection:
            # 使用 SELECT FOR UPDATE 锁定工单记录
            order = await WorkOrders.filter(id=work_order_id).select_for_update().first()
            if not order:
                raise HTTPException(status_code=404, detail="工单不存在")
            
            if order.status != 0:
                raise HTTPException(status_code=400, detail="只能签收新建状态的工单")
            
            if order.assigned_to_id:
                raise HTTPException(status_code=400, detail="工单已被其他人签收")
            
            # 更新工单信息
            order.assigned_to = current_user
            order.assigned_time = datetime.now()  # 使用系统本地时间
            order.status = 1  # 处理中
            await order.save()
            
            # 重新获取更新后的工单，包括所有关联数据
            updated_order = await WorkOrders.get(id=work_order_id).prefetch_related("assigned_to")
            return updated_order
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"工单签收失败: {str(e)}"
        )

@router.put("/{work_order_id}", response_model=WorkOrderInDB)
async def update_work_order(
    work_order_id: int,
    work_order: WorkOrderUpdate,
    current_user: Users = Depends(get_current_active_user)
):
    """更新工单"""
    try:
        order = await WorkOrders.get_or_none(id=work_order_id).prefetch_related("assigned_to")
        if not order:
            raise HTTPException(status_code=404, detail="工单不存在")
        
        # 检查权限：归档工单只有管理员可以操作
        if order.status == 3 and not current_user.is_admin:
            raise HTTPException(status_code=403, detail="归档工单仅管理员可操作")
        
        # 检查权限：非归档工单只有签收人或管理员可以更新
        if order.status != 3 and order.assigned_to_id != current_user.id and not current_user.is_admin:
            raise HTTPException(status_code=403, detail="您没有权限更新此工单")
        
        # 更新工单信息
        update_data = work_order.dict(exclude_unset=True)
        
        # 如果更新了问题类型，检查问题类型是否存在
        if "problem_type" in update_data:
            problem_type = await ProblemType.get_or_none(name=update_data["problem_type"])
            if not problem_type:
                raise HTTPException(status_code=400, detail="选择的问题类型不存在")
        
        # 如果更新了解决方案类型，检查解决方案类型是否存在
        if "solution_type" in update_data:
            solution_type = await SolutionType.get_or_none(name=update_data["solution_type"])
            if not solution_type:
                raise HTTPException(status_code=400, detail="选择的解决方案类型不存在")
        
        # 如果设置了状态为已完成(2)，检查必填字段
        if update_data.get("status") == 2:
            # 先应用更新数据
            for field, value in update_data.items():
                setattr(order, field, value)
                
            # 然后检查所有必填字段
            if not order.problem_type:
                raise HTTPException(status_code=400, detail="请选择问题类型")
            if not order.processing_desc:
                raise HTTPException(status_code=400, detail="请填写处理说明")
            if not order.solution_type:
                raise HTTPException(status_code=400, detail="请选择解决方案类型")
        else:
            # 如果不是完成状态，直接更新字段
            for field, value in update_data.items():
                setattr(order, field, value)
        
        await order.save()
        
        # 重新获取工单以包含最新的关联数据
        updated_order = await WorkOrders.get(id=work_order_id).prefetch_related("assigned_to")
        return updated_order
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"更新工单失败: {str(e)}"
        )

@router.delete("/{work_order_id}")
async def delete_work_order(
    work_order_id: int,
    current_user: Users = Depends(get_current_active_user)
):
    """删除工单（仅管理员）"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="仅管理员可以删除工单")
    
    order = await WorkOrders.get_or_none(id=work_order_id)
    if not order:
        raise HTTPException(status_code=404, detail="工单不存在")
    
    await order.delete()
    return {"message": "工单已删除"}

@router.get("/", response_model=List[WorkOrderInDB])
@router.get("", response_model=List[WorkOrderInDB])
async def get_work_orders(
    status: Optional[int] = None,
    assigned_to: Optional[int] = None,
    problem_type: Optional[str] = None,
    order_no: Optional[str] = None,
    reporter_name: Optional[str] = None,
    contact_phone: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status_lt: Optional[int] = None,
    current_user: Users = Depends(get_current_active_user)
):
    """获取工单列表"""
    query = WorkOrders.all()
    
    # 状态过滤
    if status is not None:
        query = query.filter(status=status)
    elif status_lt is not None:
        query = query.filter(status__lt=status_lt)
    
    # 签收人过滤
    if assigned_to is not None:
        query = query.filter(assigned_to_id=assigned_to)
    
    # 问题类型过滤
    if problem_type:
        query = query.filter(problem_type=problem_type)
    
    # 工单编号模糊查询
    if order_no:
        query = query.filter(order_no__icontains=order_no)

    # 报障人模糊查询
    if reporter_name:
        query = query.filter(reporter_name__icontains=reporter_name)

    # 联系电话模糊查询
    if contact_phone:
        query = query.filter(contact_phone__icontains=contact_phone)
    
    # 创建时间范围查询
    try:
        if start_date:
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
            query = query.filter(created_at__gte=start_datetime)
        if end_date:
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
            query = query.filter(created_at__lte=end_datetime)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"日期格式错误: {str(e)}"
        )
    
    # 获取工单列表
    work_orders = await query.order_by("-created_at").prefetch_related("assigned_to")
    return work_orders

@router.get("/statistics")
async def get_work_orders_statistics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status: Optional[int] = None,
    problem_type: Optional[str] = None,
    order_no: Optional[str] = None,
    assigned_to: Optional[int] = None,
    current_user: Users = Depends(get_current_active_user)
):
    """获取工单统计信息"""
    query = WorkOrders.all()
    
    # 应用过滤条件
    if status is not None:
        query = query.filter(status=status)
    if problem_type:
        query = query.filter(problem_type=problem_type)
    if order_no:
        query = query.filter(order_no__icontains=order_no)
    if assigned_to is not None:
        query = query.filter(assigned_to_id=assigned_to)
    
    # 创建时间范围查询
    try:
        if start_date:
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
            query = query.filter(created_at__gte=start_datetime)
        if end_date:
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
            query = query.filter(created_at__lte=end_datetime)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"日期格式错误: {str(e)}"
        )
    
    # 获取总数
    total = await query.count()
    
    # 获取各状态数量
    status_counts = {
        0: await query.filter(status=0).count(),
        1: await query.filter(status=1).count(),
        2: await query.filter(status=2).count(),
        3: await query.filter(status=3).count()
    }
    
    # 获取所有已定义的问题类型
    problem_types = await ProblemType.all()
    
    # 获取各类型数量
    by_type = {}
    # 先统计已定义类型的工单数量
    for type_obj in problem_types:
        count = await query.filter(problem_type=type_obj.name).count()
        by_type[type_obj.name] = count
    
    # 统计未分类的工单数量
    unclassified_count = await query.filter(Q(problem_type__isnull=True) | Q(problem_type="")).count()
    if unclassified_count > 0:
        by_type["未分类"] = unclassified_count
    
    return {
        "total": total,
        "status": status_counts,
        "by_type": by_type
    }

# 工单归档任务
async def archive_old_orders():
    # 获取系统设置中的归档时间
    settings = await SystemSettings.get_settings()
    archive_time = datetime.now() - timedelta(hours=settings.archive_hours)
    
    await WorkOrders.filter(
        status=2,  # 已完成状态
        created_at__lt=archive_time,
        archived_at__isnull=True
    ).update(
        status=3,  # 归档状态
        archived_at=datetime.now()
    )

@router.get("/{work_order_id}", response_model=WorkOrderInDB)
async def get_work_order(
    work_order_id: int,
    current_user: Users = Depends(get_current_active_user)
):
    """获取工单详情"""
    try:
        order = await WorkOrders.get_or_none(id=work_order_id).prefetch_related("assigned_to")
        if not order:
            raise HTTPException(status_code=404, detail="工单不存在")
        return order
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取工单详情失败: {str(e)}"
        )

@router.get("/{work_order_id}/logs")
async def get_work_order_logs(
    work_order_id: int,
    current_user: Users = Depends(get_current_active_user)
):
    """获取工单日志"""
    # 由于目前没有日志表，先返回空列表
    return []

@router.post("/archive")
async def trigger_archive(
    current_user: Users = Depends(get_current_active_user)
):
    """触发自动归档"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    # 获取系统设置中的归档时间
    settings = await SystemSettings.get_settings()
    archive_hours = settings.archive_hours
    
    # 计算需要归档的时间点
    archive_time = datetime.now() - timedelta(hours=archive_hours)
    
    # 查找需要归档的工单（已完成且超过归档时间的工单）
    orders = await WorkOrders.filter(
        status=2,  # 已完成状态
        modified_at__lt=archive_time,  # 最后修改时间早于归档时间
        archived_at__isnull=True  # 尚未归档
    )
    
    # 批量更新状态为已归档
    archived_count = 0
    for order in orders:
        order.status = 3
        order.archived_at = datetime.now()
        await order.save()
        archived_count += 1
    
    return {"message": f"成功归档 {archived_count} 个工单"} 