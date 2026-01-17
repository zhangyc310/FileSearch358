"""
Whoosh 全文搜索引擎
支持文件内容和文件名索引
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Callable, Optional
from datetime import datetime

from whoosh import index
from whoosh.fields import Schema, TEXT, ID, DATETIME, STORED
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.writing import AsyncWriter
from whoosh.analysis import StemmingAnalyzer
from whoosh.query import Term

from .document_parser import DocumentParser

logger = logging.getLogger(__name__)


class SearchEngine:
    """搜索引擎类"""

    def __init__(self, index_dir: str = "index"):
        """
        初始化搜索引擎

        Args:
            index_dir: 索引存储目录
        """
        self.index_dir = index_dir
        self.parser = DocumentParser()
        self.ix = None

        # 确保索引目录存在
        os.makedirs(index_dir, exist_ok=True)

        # 创建或打开索引
        self._init_index()

    def _init_index(self):
        """初始化索引"""
        # 定义索引结构
        schema = Schema(
            path=ID(stored=True, unique=True),  # 文件路径（唯一标识）
            filename=TEXT(stored=True, analyzer=StemmingAnalyzer()),  # 文件名
            content=TEXT(analyzer=StemmingAnalyzer()),  # 文件内容
            extension=STORED(),  # 文件扩展名
            size=STORED(),  # 文件大小
            modified=DATETIME(stored=True),  # 修改时间
            has_content=STORED()  # 是否包含内容索引
        )

        # 如果索引存在则打开，否则创建
        if index.exists_in(self.index_dir):
            self.ix = index.open_dir(self.index_dir)
            logger.info("打开现有索引")
        else:
            self.ix = index.create_in(self.index_dir, schema)
            logger.info("创建新索引")

    def index_directory(
        self,
        directory: str,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> Dict[str, int]:
        """
        索引整个目录

        Args:
            directory: 要索引的目录路径
            progress_callback: 进度回调函数 (当前数, 总数, 文件名)

        Returns:
            索引统计信息
        """
        stats = {
            'total': 0,
            'indexed': 0,
            'content_indexed': 0,
            'filename_only': 0,
            'errors': 0
        }

        # 收集所有文件
        files = []
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                files.append(file_path)

        stats['total'] = len(files)
        logger.info(f"找到 {len(files)} 个文件")

        # 索引文件
        writer = AsyncWriter(self.ix)

        try:
            for idx, file_path in enumerate(files, 1):
                try:
                    # 回调进度
                    if progress_callback:
                        progress_callback(idx, stats['total'], file_path)

                    # 索引文件
                    if self._index_file(writer, file_path):
                        stats['indexed'] += 1

                        # 统计内容索引
                        if self.parser.can_extract_content(file_path):
                            stats['content_indexed'] += 1
                        else:
                            stats['filename_only'] += 1

                except Exception as e:
                    logger.error(f"索引文件失败 {file_path}: {e}")
                    stats['errors'] += 1

            writer.commit()
            logger.info(f"索引完成: {stats}")

        except Exception as e:
            logger.error(f"索引过程出错: {e}")
            writer.cancel()

        return stats

    def _index_file(self, writer, file_path: str) -> bool:
        """
        索引单个文件

        Args:
            writer: Whoosh 写入器
            file_path: 文件路径

        Returns:
            是否成功索引
        """
        try:
            path_obj = Path(file_path)
            filename = path_obj.name
            extension = path_obj.suffix.lower()

            # 获取文件信息
            stat = os.stat(file_path)
            size = stat.st_size
            modified = datetime.fromtimestamp(stat.st_mtime)

            # 提取内容（如果支持）
            content = ""
            has_content = False

            if self.parser.can_extract_content(file_path):
                content = self.parser.extract_text(file_path)
                if content:
                    has_content = True
                    logger.debug(f"提取内容: {filename} ({len(content)} 字符)")

            # 添加到索引
            writer.update_document(
                path=file_path,
                filename=filename,
                content=content or "",
                extension=extension,
                size=size,
                modified=modified,
                has_content=has_content
            )

            return True

        except Exception as e:
            logger.error(f"索引文件失败 {file_path}: {e}")
            return False

    def search(
        self,
        query_text: str,
        search_type: str = "content",
        limit: int = 100
    ) -> List[Dict]:
        """
        搜索文件

        Args:
            query_text: 查询文本
            search_type: 搜索类型 ("content" 或 "filename")
            limit: 最大返回结果数

        Returns:
            搜索结果列表
        """
        if not query_text.strip():
            return []

        results = []

        try:
            with self.ix.searcher() as searcher:
                # 根据搜索类型选择查询解析器
                if search_type == "content":
                    # 搜索内容（同时搜索文件名和内容）
                    parser = MultifieldParser(
                        ["filename", "content"],
                        schema=self.ix.schema
                    )
                else:
                    # 仅搜索文件名
                    parser = QueryParser("filename", schema=self.ix.schema)

                query = parser.parse(query_text)
                search_results = searcher.search(query, limit=limit)

                # 处理结果
                for hit in search_results:
                    results.append({
                        'path': hit['path'],
                        'filename': hit['filename'],
                        'extension': hit.get('extension', ''),
                        'size': hit.get('size', 0),
                        'modified': hit.get('modified'),
                        'has_content': hit.get('has_content', False),
                        'score': hit.score
                    })

        except Exception as e:
            logger.error(f"搜索失败: {e}")

        return results

    def delete_file(self, file_path: str):
        """
        从索引中删除文件

        Args:
            file_path: 文件路径
        """
        try:
            writer = self.ix.writer()
            writer.delete_by_term('path', file_path)
            writer.commit()
            logger.debug(f"从索引删除: {file_path}")
        except Exception as e:
            logger.error(f"删除索引失败 {file_path}: {e}")

    def update_file(self, file_path: str):
        """
        更新文件索引

        Args:
            file_path: 文件路径
        """
        try:
            writer = self.ix.writer()
            self._index_file(writer, file_path)
            writer.commit()
            logger.debug(f"更新索引: {file_path}")
        except Exception as e:
            logger.error(f"更新索引失败 {file_path}: {e}")

    def clear_index(self):
        """清空所有索引"""
        try:
            writer = self.ix.writer()
            writer.commit(mergetype=index.CLEAR)
            logger.info("索引已清空")
        except Exception as e:
            logger.error(f"清空索引失败: {e}")

    def get_stats(self) -> Dict:
        """
        获取索引统计信息

        Returns:
            统计信息字典
        """
        try:
            with self.ix.searcher() as searcher:
                doc_count = searcher.doc_count_all()
                return {
                    'total_documents': doc_count,
                    'index_size': self._get_index_size()
                }
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {'total_documents': 0, 'index_size': 0}

    def _get_index_size(self) -> int:
        """获取索引文件大小（字节）"""
        total_size = 0
        try:
            for root, _, files in os.walk(self.index_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    total_size += os.path.getsize(file_path)
        except Exception as e:
            logger.error(f"计算索引大小失败: {e}")
        return total_size


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)

    engine = SearchEngine()

    # 测试索引
    stats = engine.index_directory(".", lambda cur, total, name: print(f"{cur}/{total}: {name}"))
    print(f"索引统计: {stats}")

    # 测试搜索
    results = engine.search("test", search_type="filename")
    print(f"搜索结果: {len(results)} 个")
    for r in results[:5]:
        print(f"  - {r['filename']}")
