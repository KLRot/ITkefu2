"""
测试解决方案类型功能
"""
import asyncio
import logging
from tortoise import Tortoise
from app.models.models import SolutionType, WorkOrders

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def init_db():
    # 初始化数据库连接
    await Tortoise.init(
        db_url="sqlite://data/itkefu.db",
        modules={"models": ["app.models.models"]}
    )

async def test_solution_types():
    """测试解决方案类型功能"""
    try:
        # 1. 创建一些测试解决方案类型
        test_types = ["硬件更换", "软件重装", "网络配置", "系统优化"]
        created_types = []
        
        # 先清理已存在的测试类型
        for type_name in test_types:
            existing = await SolutionType.get_or_none(name=type_name)
            if existing:
                await existing.delete()
                logger.info(f"删除已存在的解决方案类型: {type_name}")
        
        # 创建新的测试类型
        for type_name in test_types:
            solution_type = await SolutionType.create(name=type_name)
            created_types.append(solution_type)
            logger.info(f"创建测试解决方案类型: {type_name}")
        
        # 2. 获取所有解决方案类型并验证
        all_types = await SolutionType.all()
        logger.info(f"系统中共有 {len(all_types)} 个解决方案类型")
        
        # 验证我们刚创建的测试类型是否存在
        for created_type in created_types:
            found = False
            for db_type in all_types:
                if db_type.name == created_type.name:
                    found = True
                    break
            
            if found:
                logger.info(f"√ 验证通过: 找到解决方案类型 '{created_type.name}'")
            else:
                logger.error(f"× 验证失败: 未找到解决方案类型 '{created_type.name}'")
        
        # 3. 获取一个工单并设置解决方案类型
        work_order = await WorkOrders.first()
        if work_order:
            original_type = work_order.solution_type
            logger.info(f"获取到工单: {work_order.order_no}, 原解决方案类型: {original_type}")
            
            # 设置为第一个测试类型
            work_order.solution_type = test_types[0]
            await work_order.save(update_fields=["solution_type"])
            logger.info(f"设置工单解决方案类型为: {test_types[0]}")
            
            # 重新获取并验证
            updated_order = await WorkOrders.get(id=work_order.id)
            if updated_order.solution_type == test_types[0]:
                logger.info(f"√ 验证通过: 工单解决方案类型已更新为 '{test_types[0]}'")
            else:
                logger.error(f"× 验证失败: 工单解决方案类型更新失败")
            
            # 恢复原状态
            work_order.solution_type = original_type
            await work_order.save(update_fields=["solution_type"])
            logger.info(f"恢复工单原解决方案类型: {original_type}")
        else:
            logger.warning("没有找到工单进行测试")
        
        logger.info("测试完成")
    except Exception as e:
        logger.error(f"测试过程中出错: {str(e)}")
        raise

async def run_test():
    """运行测试"""
    logger.info("开始测试...")
    await init_db()
    await test_solution_types()
    await Tortoise.close_connections()
    logger.info("测试结束")

if __name__ == "__main__":
    asyncio.run(run_test()) 