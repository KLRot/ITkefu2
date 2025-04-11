from pydantic import BaseModel, Field, constr
from typing import Optional
from datetime import datetime

class ProblemTypeInfo(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True

class UserInfo(BaseModel):
    id: int
    username: str
    full_name: str
    
    class Config:
        from_attributes = True

class WorkOrderBase(BaseModel):
    reporter_name: str
    contact_phone: str
    location: str
    problem_desc: str

class WorkOrderCreate(WorkOrderBase):
    pass

class WorkOrderUpdate(BaseModel):
    status: Optional[int] = None
    problem_type: Optional[str] = None
    processing_desc: Optional[str] = None
    solution_type: Optional[str] = None

class WorkOrderAssign(BaseModel):
    pass  # 不需要任何字段，因为我们使用当前登录用户作为签收人

class WorkOrderInDB(WorkOrderBase):
    id: int
    order_no: str
    status: int
    problem_type: Optional[str] = None
    assigned_to: Optional[UserInfo] = None
    assigned_time: Optional[datetime] = None
    processing_desc: Optional[str] = None
    solution_type: Optional[str] = None
    created_at: datetime
    modified_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda dt: dt.strftime("%Y-%m-%d %H:%M:%S") if dt else None
        }

class WorkOrderLogCreate(BaseModel):
    work_order_id: int
    action: str
    status_from: int
    status_to: int
    remark: str 