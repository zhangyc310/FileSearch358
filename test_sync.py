"""
增量同步功能测试脚本

演示场景：
1. 创建测试目录并索引
2. 模拟停用一段时间
3. 添加、修改、删除文件
4. 测试智能同步功能
"""

import os
import sys
import time
import shutil
import logging
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.indexer.search_engine import SearchEngine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_test_environment():
    """创建测试环境"""
    test_dir = "test_sync_demo"
    index_dir = "test_sync_index"

    # 清理旧的测试环境
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    if os.path.exists(index_dir):
        shutil.rmtree(index_dir)

    # 创建测试目录
    os.makedirs(test_dir)

    # 创建初始文件
    files = {
        "文档1.txt": "这是第一个文档，包含关键词Python和机器学习",
        "文档2.txt": "这是第二个文档，讨论深度学习框架",
        "README.md": "# 项目说明\n这是一个测试项目",
        "数据分析.txt": "使用pandas进行数据分析",
    }

    for filename, content in files.items():
        filepath = os.path.join(test_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

    logger.info(f"✅ 创建测试目录: {test_dir}")
    logger.info(f"   创建了 {len(files)} 个文件")

    return test_dir, index_dir


def initial_index(engine, test_dir):
    """初始索引"""
    logger.info("\n" + "=" * 60)
    logger.info("步骤 1: 初始索引")
    logger.info("=" * 60)

    stats = engine.index_directory(test_dir)

    logger.info(f"✅ 索引完成:")
    logger.info(f"   总文件: {stats['total']}")
    logger.info(f"   成功索引: {stats['indexed']}")
    logger.info(f"   内容索引: {stats['content_indexed']}")

    return stats


def simulate_changes(test_dir):
    """模拟文件变化"""
    logger.info("\n" + "=" * 60)
    logger.info("步骤 2: 模拟停用期间的文件变化")
    logger.info("=" * 60)

    time.sleep(2)  # 确保时间戳不同

    changes = []

    # 1. 新增文件
    new_file = os.path.join(test_dir, "新文档.txt")
    with open(new_file, 'w', encoding='utf-8') as f:
        f.write("这是停用期间新增的文档")
    changes.append(("新增", "新文档.txt"))
    logger.info("📄 新增文件: 新文档.txt")

    # 2. 修改文件
    modified_file = os.path.join(test_dir, "文档1.txt")
    with open(modified_file, 'a', encoding='utf-8') as f:
        f.write("\n\n更新内容：添加了关于TensorFlow的讨论")
    changes.append(("修改", "文档1.txt"))
    logger.info("🔄 修改文件: 文档1.txt")

    # 3. 删除文件
    deleted_file = os.path.join(test_dir, "数据分析.txt")
    os.remove(deleted_file)
    changes.append(("删除", "数据分析.txt"))
    logger.info("🗑️ 删除文件: 数据分析.txt")

    # 4. 再新增一个文件
    another_new = os.path.join(test_dir, "教程.md")
    with open(another_new, 'w', encoding='utf-8') as f:
        f.write("# 教程\n\n如何使用Python进行Web开发")
    changes.append(("新增", "教程.md"))
    logger.info("📄 新增文件: 教程.md")

    logger.info(f"\n总共模拟了 {len(changes)} 个文件变化")

    return changes


def test_sync(engine, test_dir):
    """测试同步功能"""
    logger.info("\n" + "=" * 60)
    logger.info("步骤 3: 执行智能同步")
    logger.info("=" * 60)

    def progress_callback(current, total, description):
        logger.info(f"   进度: {current}/{total} - {description}")

    stats = engine.sync_directory(test_dir, progress_callback)

    logger.info(f"\n✅ 同步完成:")
    logger.info(f"   扫描文件: {stats['scanned']}")
    logger.info(f"   新增: {stats['added']}")
    logger.info(f"   更新: {stats['updated']}")
    logger.info(f"   删除: {stats['deleted']}")
    logger.info(f"   未变化: {stats['unchanged']}")
    logger.info(f"   错误: {stats['errors']}")

    return stats


def verify_search(engine):
    """验证搜索功能"""
    logger.info("\n" + "=" * 60)
    logger.info("步骤 4: 验证搜索功能")
    logger.info("=" * 60)

    test_queries = [
        ("Python", "应该能找到修改后的文档1和新文档"),
        ("TensorFlow", "应该能找到修改后的文档1"),
        ("数据分析", "应该找不到（已删除）"),
        ("Web开发", "应该能找到新增的教程.md"),
    ]

    for query, expected in test_queries:
        results = engine.search(query, search_type="content")
        logger.info(f"\n🔍 搜索: '{query}'")
        logger.info(f"   预期: {expected}")
        logger.info(f"   结果: 找到 {len(results)} 个文件")
        for r in results:
            logger.info(f"      - {r['filename']}")


def cleanup(test_dir, index_dir):
    """清理测试环境"""
    logger.info("\n" + "=" * 60)
    logger.info("清理测试环境")
    logger.info("=" * 60)

    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
        logger.info(f"✅ 删除测试目录: {test_dir}")

    if os.path.exists(index_dir):
        shutil.rmtree(index_dir)
        logger.info(f"✅ 删除索引目录: {index_dir}")


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("增量同步功能测试")
    logger.info("=" * 60)

    # 创建测试环境
    test_dir, index_dir = create_test_environment()

    try:
        # 创建搜索引擎
        engine = SearchEngine(index_dir=index_dir)

        # 步骤 1: 初始索引
        initial_index(engine, test_dir)

        # 模拟程序停用
        logger.info("\n💤 模拟程序停用...")
        time.sleep(1)

        # 步骤 2: 模拟文件变化
        simulate_changes(test_dir)

        # 模拟程序重新启动
        logger.info("\n🚀 模拟程序重新启动...")
        time.sleep(1)

        # 步骤 3: 测试同步
        sync_stats = test_sync(engine, test_dir)

        # 验证同步结果
        expected_added = 2
        expected_updated = 1
        expected_deleted = 1

        if (sync_stats['added'] == expected_added and
            sync_stats['updated'] == expected_updated and
            sync_stats['deleted'] == expected_deleted):
            logger.info("\n✅✅✅ 同步测试通过！")
        else:
            logger.error("\n❌ 同步测试失败！")
            logger.error(f"   期望: 新增{expected_added}, 更新{expected_updated}, 删除{expected_deleted}")
            logger.error(f"   实际: 新增{sync_stats['added']}, 更新{sync_stats['updated']}, 删除{sync_stats['deleted']}")

        # 步骤 4: 验证搜索
        verify_search(engine)

        logger.info("\n" + "=" * 60)
        logger.info("✅ 所有测试完成！")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"\n❌ 测试失败: {e}", exc_info=True)

    finally:
        # 清理
        cleanup(test_dir, index_dir)


if __name__ == "__main__":
    main()
