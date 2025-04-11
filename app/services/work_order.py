from datetime import datetime
import random
import string
from typing import List, Optional
from app.models.models import WorkOrders, Users

def generate_order_no() -> str:
    """生成工单编号"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"WO{timestamp}{random_str}"

class WorkOrderService:
    @staticmethod
    async def create_work_order(
        reporter_name: str,
        contact_phone: str,
        location: str,
        problem_desc: str,
        problem_type: int,
        priority: int
    ) -> WorkOrders:
        """创建工单"""
        order_no = generate_order_no()
        work_order = await WorkOrders.create(
            order_no=order_no,
            reporter_name=reporter_name,
            contact_phone=contact_phone,
            location=location,
            problem_desc=problem_desc,
            problem_type=problem_type,
            priority=priority,
            status=0  # 新建状态
        )
        return work_order

    @staticmethod
    async def assign_work_order(
        work_order_id: int,
        assigned_to: int,
        operator_id: int
    ) -> WorkOrders:
        """分配工单"""
        work_order = await WorkOrders.get(id=work_order_id)
        
        # 更新工单
        work_order.assigned_to_id = assigned_to
        work_order.assigned_time = datetime.now()
        work_order.status = 1  # 已分配状态
        await work_order.save()
        
        return work_order

    @staticmethod
    async def update_work_order(
        work_order_id: int,
        operator_id: int,
        status: Optional[int] = None,
        processing_desc: Optional[str] = None,
        solution: Optional[str] = None
    ) -> WorkOrders:
        """更新工单"""
        work_order = await WorkOrders.get(id=work_order_id)
        
        if status is not None:
            work_order.status = status
        if processing_desc is not None:
            work_order.processing_desc = processing_desc
        if solution is not None:
            work_order.solution = solution
            
        await work_order.save()
        
        return work_order

    @staticmethod
    async def get_work_orders(
        status: Optional[int] = None,
        assigned_to: Optional[int] = None,
        problem_type: Optional[int] = None
    ) -> List[WorkOrders]:
        """查询工单列表"""
        query = WorkOrders.all()
        
        if status is not None:
            query = query.filter(status=status)
        if assigned_to is not None:
            query = query.filter(assigned_to_id=assigned_to)
        if problem_type is not None:
            query = query.filter(problem_type=problem_type)
            
        return await query.order_by("-created_at")

    @staticmethod
    async def get_work_order_statistics():
        """获取工单统计信息"""
        total = await WorkOrders.all().count()
        pending = await WorkOrders.filter(status=0).count()
        processing = await WorkOrders.filter(status=2).count()
        completed = await WorkOrders.filter(status=3).count()
        
        by_type = {}
        for type_id in range(1, 5):  # 1-4: 硬件、软件、网络、账号
            count = await WorkOrders.filter(problem_type=type_id).count()
            by_type[type_id] = count
        
        return {
            "total": total,
            "status": {
                "pending": pending,
                "processing": processing,
                "completed": completed
            },
            "by_type": by_type
        } 