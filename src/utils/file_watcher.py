"""
文件监控模块
自动监控文件变化并更新索引
"""

import os
import logging
from pathlib import Path
from typing import Optional

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

logger = logging.getLogger(__name__)


class IndexFileHandler(FileSystemEventHandler):
    """文件系统事件处理器"""

    def __init__(self, search_engine):
        """
        初始化事件处理器

        Args:
            search_engine: 搜索引擎实例
        """
        super().__init__()
        self.search_engine = search_engine

    def on_created(self, event: FileSystemEvent):
        """文件创建事件"""
        if not event.is_directory:
            logger.info(f"文件创建: {event.src_path}")
            self.search_engine.update_file(event.src_path)

    def on_modified(self, event: FileSystemEvent):
        """文件修改事件"""
        if not event.is_directory:
            logger.info(f"文件修改: {event.src_path}")
            self.search_engine.update_file(event.src_path)

    def on_deleted(self, event: FileSystemEvent):
        """文件删除事件"""
        if not event.is_directory:
            logger.info(f"文件删除: {event.src_path}")
            self.search_engine.delete_file(event.src_path)

    def on_moved(self, event: FileSystemEvent):
        """文件移动事件"""
        if not event.is_directory:
            logger.info(f"文件移动: {event.src_path} -> {event.dest_path}")
            self.search_engine.delete_file(event.src_path)
            self.search_engine.update_file(event.dest_path)


class FileWatcher:
    """文件监控器"""

    def __init__(self, search_engine):
        """
        初始化文件监控器

        Args:
            search_engine: 搜索引擎实例
        """
        self.search_engine = search_engine
        self.observer: Optional[Observer] = None
        self.watched_directory: Optional[str] = None

    def start_watching(self, directory: str):
        """
        开始监控目录

        Args:
            directory: 要监控的目录路径
        """
        if not os.path.exists(directory):
            logger.error(f"目录不存在: {directory}")
            return False

        # 停止现有监控
        if self.observer and self.observer.is_alive():
            self.stop_watching()

        # 创建新的监控器
        self.observer = Observer()
        event_handler = IndexFileHandler(self.search_engine)

        self.observer.schedule(event_handler, directory, recursive=True)
        self.observer.start()

        self.watched_directory = directory
        logger.info(f"开始监控目录: {directory}")

        return True

    def stop_watching(self):
        """停止监控"""
        if self.observer and self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
            logger.info(f"停止监控: {self.watched_directory}")
            self.watched_directory = None

    def is_watching(self) -> bool:
        """检查是否正在监控"""
        return self.observer is not None and self.observer.is_alive()


if __name__ == "__main__":
    # 测试代码
    from ..indexer.search_engine import SearchEngine

    logging.basicConfig(level=logging.INFO)

    engine = SearchEngine()
    watcher = FileWatcher(engine)

    # 监控当前目录
    watcher.start_watching(".")

    try:
        import time
        print("监控中... 按 Ctrl+C 停止")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        watcher.stop_watching()
        print("已停止监控")
