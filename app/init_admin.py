import asyncio
from app.models.models import Users
from app.core.security import get_password_hash
from tortoise import Tortoise
from app.main import TORTOISE_ORM

async def init():
    # 初始化数据库连接
    await Tortoise.init(config=TORTOISE_ORM)
    
    # 创建数据库表
    await Tortoise.generate_schemas()
    
    # 检查是否已存在管理员用户
    admin = await Users.filter(username="admin").first()
    if not admin:
        # 创建管理员用户
        await Users.create(
            username="admin",
            password_hash=get_password_hash("admin123"),
            full_name="系统管理员",
            is_admin=True
        )
        print("管理员用户创建成功！")
    else:
        print("管理员用户已存在！")
    
    # 关闭数据库连接
    await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(init()) 