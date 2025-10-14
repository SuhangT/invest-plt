"""数据库初始化脚本"""
from app import app, db
from models import Index, SystemConfig
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_database():
    """初始化数据库"""
    with app.app_context():
        logger.info("开始初始化数据库...")
        
        # 创建所有表
        db.create_all()
        logger.info("数据库表创建成功")
        
        # 添加默认配置
        config = SystemConfig.query.filter_by(key='data_initialized').first()
        if not config:
            config = SystemConfig(
                key='data_initialized',
                value='false',
                description='数据是否已初始化'
            )
            db.session.add(config)
            db.session.commit()
            logger.info("默认配置添加成功")
        
        logger.info("数据库初始化完成")


if __name__ == '__main__':
    init_database()
