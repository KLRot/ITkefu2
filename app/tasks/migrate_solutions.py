"""
数据库迁移脚本: 删除优先级字段，将解决方案迁移到解决方案类型
"""
import asyncio
import logging
from tortoise import Tortoise
from app.models.models import WorkOrders, SolutionType

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def init_db():
    # 初始化数据库连接
    await Tortoise.init(
        db_url="sqlite://data/itkefu.db",
        modules={"models": ["app.models.models"]}
    )

async def migrate_solution_data():
    """
    将现有工单的 solution 字段数据迁移到 solution_type 字段，
    并创建必要的解决方案类型记录
    """
    try:
        # 获取所有有解决方案的工单
        orders = await WorkOrders.filter(solution__not_isnull=True).all()
        logger.info(f"找到 {len(orders)} 个有解决方案的工单")

        # 收集所有不同的解决方案
        unique_solutions = {}
        for order in orders:
            if order.solution and order.solution.strip():
                solution_text = order.solution.strip()
                # 如果解决方案超过50个字符，使用前50个字符作为类型名称
                type_name = solution_text[:50] if len(solution_text) > 50 else solution_text
                if type_name not in unique_solutions:
                    unique_solutions[type_name] = []
                unique_solutions[type_name].append(order.id)

        logger.info(f"找到 {len(unique_solutions)} 个唯一解决方案")

        # 为每个唯一解决方案创建解决方案类型
        for solution_name, order_ids in unique_solutions.items():
            # 检查是否已存在相同名称的解决方案类型
            existing = await SolutionType.get_or_none(name=solution_name)
            if not existing:
                # 创建新的解决方案类型
                await SolutionType.create(name=solution_name)
                logger.info(f"创建新解决方案类型: {solution_name}")
            
            # 更新相关工单的解决方案类型
            for order_id in order_ids:
                order = await WorkOrders.get(id=order_id)
                order.solution_type = solution_name
                await order.save(update_fields=["solution_type"])
            
            logger.info(f"已更新 {len(order_ids)} 个工单使用解决方案类型: {solution_name}")

        logger.info("数据迁移完成")
    except Exception as e:
        logger.error(f"迁移过程中出错: {str(e)}")
        raise

async def run_migration():
    """运行迁移流程"""
    logger.info("开始迁移过程...")
    await init_db()
    await migrate_solution_data()
    await Tortoise.close_connections()
    logger.info("迁移完成")

if __name__ == "__main__":
    asyncio.run(run_migration()) 