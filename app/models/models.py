from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from datetime import datetime

class Users(models.Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True)
    password_hash = fields.CharField(max_length=128)
    full_name = fields.CharField(max_length=50)
    is_active = fields.BooleanField(default=True)
    is_admin = fields.BooleanField(default=False)
    created_at = fields.DatetimeField()

    async def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.now()
        await super().save(*args, **kwargs)

    class Meta:
        table = "users"

class SystemSettings(models.Model):
    id = fields.IntField(pk=True)
    archive_hours = fields.IntField(default=72)  # 默认72小时后归档
    created_at = fields.DatetimeField()
    modified_at = fields.DatetimeField()

    async def save(self, *args, **kwargs):
        current_time = datetime.now()
        if not self.created_at:
            self.created_at = current_time
        self.modified_at = current_time
        await super().save(*args, **kwargs)

    @classmethod
    async def get_settings(cls):
        settings = await cls.first()
        if not settings:
            settings = await cls.create(archive_hours=72)
        return settings

    @classmethod
    async def update_settings(cls, archive_hours: int):
        """更新系统设置"""
        settings = await cls.get_settings()
        settings.archive_hours = archive_hours
        await settings.save()
        return settings

    class Meta:
        table = "system_settings"

class ProblemType(models.Model):
    """问题类型"""
    name = fields.CharField(max_length=50, unique=True)

    class Meta:
        table = "problem_types"

class SolutionType(models.Model):
    """解决方案类型"""
    name = fields.CharField(max_length=50, unique=True)
    
    class Meta:
        table = "solution_types"

class WorkOrders(models.Model):
    id = fields.IntField(pk=True)
    order_no = fields.CharField(max_length=20, unique=True)  # SZIT-20250224-001 格式
    reporter_name = fields.CharField(max_length=255)
    contact_phone = fields.CharField(max_length=255)
    location = fields.TextField()
    problem_desc = fields.TextField()
    problem_type = fields.CharField(max_length=255, null=True)  # 修改为直接存储类型名称
    status = fields.IntField(default=0)  # 0:新建, 1:处理中, 2:已完成, 3:已归档
    assigned_to = fields.ForeignKeyField('models.Users', related_name='assigned_orders', null=True)
    assigned_time = fields.DatetimeField(null=True)  # 签收时间
    processing_desc = fields.TextField(null=True)  # 处理说明
    solution_type = fields.CharField(max_length=255, null=True)  # 解决方案类型
    created_at = fields.DatetimeField()
    modified_at = fields.DatetimeField()
    archived_at = fields.DatetimeField(null=True)  # 归档时间

    async def save(self, *args, **kwargs):
        # 获取当前时间
        current_time = datetime.now()
        
        # 如果是新记录，设置创建时间
        if not self.created_at:
            self.created_at = current_time
            
        # 每次保存都更新修改时间
        self.modified_at = current_time
        
        # 获取当前对象的原始状态（如果存在）
        if self.id:
            old_order = await WorkOrders.get(id=self.id)
            old_status = old_order.status
            old_assigned_to = old_order.assigned_to_id
        else:
            old_status = None
            old_assigned_to = None

        # 如果是签收操作（状态从0变为1，或assigned_to从None变为有值）
        if ((old_status == 0 and self.status == 1) or 
            (old_assigned_to is None and self.assigned_to_id is not None)):
            self.assigned_time = current_time

        # 如果状态变更为已归档
        if self.status == 3 and (old_status != 3 or not self.archived_at):
            self.archived_at = current_time
            
        await super().save(*args, **kwargs)

    class Meta:
        table = "work_orders"

# 创建 Pydantic 模型
User_Pydantic = pydantic_model_creator(Users, name="User")
UserIn_Pydantic = pydantic_model_creator(Users, name="UserIn", exclude_readonly=True)

WorkOrder_Pydantic = pydantic_model_creator(
    WorkOrders,
    name="WorkOrder",
    exclude=("assigned_to",)
)
WorkOrderIn_Pydantic = pydantic_model_creator(
    WorkOrders,
    name="WorkOrderIn",
    exclude_readonly=True,
    exclude=("assigned_to",)
) 