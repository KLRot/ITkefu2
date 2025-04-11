from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from tortoise.contrib.fastapi import register_tortoise
from app.core.config import settings
from app.api import auth, work_orders, settings as settings_api
from app.tasks.archive import setup_archive_scheduler

app = FastAPI(
    title="客服派单平台",
    description="轻量级的客服派单平台API",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# 注册路由
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["认证"])
app.include_router(work_orders.router, prefix=f"{settings.API_V1_STR}/work-orders", tags=["工单"])
app.include_router(settings_api.router, prefix=f"{settings.API_V1_STR}/settings", tags=["系统设置"])

# 数据库配置
TORTOISE_ORM = {
    "connections": {"default": settings.DATABASE_URL},
    "apps": {
        "models": {
            "models": ["app.models.models"],
            "default_connection": "default",
        },
    },
}

# 注册数据库
register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,
    add_exception_handlers=True,
)

# 启动定时任务
@app.on_event("startup")
async def startup_event():
    setup_archive_scheduler()

@app.get("/")
async def root():
    return {"message": "欢迎使用客服派单平台API"} 