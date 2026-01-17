"""
模块测试脚本
"""

import os
import sys
import logging
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.indexer.document_parser import DocumentParser
from src.indexer.search_engine import SearchEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_document_parser():
    """测试文档解析器"""
    logger.info("=" * 50)
    logger.info("测试文档解析器")
    logger.info("=" * 50)

    parser = DocumentParser()

    # 创建测试文本文件
    test_file = "test_sample.txt"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write("这是一个测试文件\n包含中文和English\n用于测试文档解析功能")

    # 测试提取
    content = parser.extract_text(test_file)
    logger.info(f"提取内容: {content}")

    # 测试文件类型判断
    logger.info(f"支持内容提取: {parser.can_extract_content(test_file)}")
    logger.info(f"是否为媒体文件: {parser.is_media_file('test.mp4')}")

    # 清理
    os.remove(test_file)

    logger.info("✅ 文档解析器测试完成\n")


def test_search_engine():
    """测试搜索引擎"""
    logger.info("=" * 50)
    logger.info("测试搜索引擎")
    logger.info("=" * 50)

    # 创建测试目录
    test_dir = "test_files"
    os.makedirs(test_dir, exist_ok=True)

    # 创建测试文件
    test_files = [
        ("文档1.txt", "这是第一个测试文档，包含关键词Python"),
        ("文档2.txt", "这是第二个测试文档，包含关键词Java"),
        ("README.md", "# 项目说明\n这是一个Python项目"),
    ]

    for filename, content in test_files:
        filepath = os.path.join(test_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

    # 创建搜索引擎
    engine = SearchEngine(index_dir="test_index")

    # 索引文件
    logger.info(f"开始索引目录: {test_dir}")
    stats = engine.index_directory(test_dir)
    logger.info(f"索引统计: {stats}")

    # 测试搜索
    logger.info("\n测试搜索 'Python':")
    results = engine.search("Python", search_type="content")
    logger.info(f"找到 {len(results)} 个结果")
    for r in results:
        logger.info(f"  - {r['filename']} (相关度: {r['score']:.2f})")

    logger.info("\n测试文件名搜索 '文档':")
    results = engine.search("文档", search_type="filename")
    logger.info(f"找到 {len(results)} 个结果")
    for r in results:
        logger.info(f"  - {r['filename']}")

    # 获取统计信息
    stats = engine.get_stats()
    logger.info(f"\n索引统计: {stats}")

    # 清理
    import shutil
    shutil.rmtree(test_dir, ignore_errors=True)
    shutil.rmtree("test_index", ignore_errors=True)

    logger.info("✅ 搜索引擎测试完成\n")


def main():
    """运行所有测试"""
    logger.info("开始测试 FileSearch 模块")
    logger.info("=" * 50)

    try:
        test_document_parser()
        test_search_engine()

        logger.info("=" * 50)
        logger.info("✅ 所有测试完成！")
        logger.info("=" * 50)

    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
