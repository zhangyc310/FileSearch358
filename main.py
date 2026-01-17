"""
FileSearch - 文档全文搜索工具
主入口文件
"""

import sys
import logging
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.ui.main_window import run_app


def setup_logging():
    """配置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('filesearch.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )


def main():
    """主函数"""
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("启动 FileSearch 应用")

    try:
        run_app()
    except Exception as e:
        logger.error(f"应用运行出错: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
