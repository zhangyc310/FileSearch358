"""
CustomTkinter 主界面
"""

import os
import threading
import logging
from pathlib import Path
from typing import Optional

import customtkinter as ctk
from tkinter import filedialog, messagebox

from ..indexer.search_engine import SearchEngine

logger = logging.getLogger(__name__)


class MainWindow(ctk.CTk):
    """主窗口类"""

    def __init__(self):
        super().__init__()

        # 配置窗口
        self.title("📁 FileSearch - 文档搜索工具")
        self.geometry("900x700")

        # 设置主题
        ctk.set_appearance_mode("dark")  # 或 "light"
        ctk.set_default_color_theme("blue")

        # 初始化搜索引擎
        self.search_engine = SearchEngine()
        self.current_directory: Optional[str] = None
        self.indexing_thread: Optional[threading.Thread] = None

        # 创建 UI
        self._create_ui()

        # 加载统计信息
        self._update_stats()

        # 检查是否需要同步（延迟执行，等待窗口显示）
        self.after(500, self._check_sync_on_startup)

    def _create_ui(self):
        """创建用户界面"""

        # ===== 顶部区域 =====
        top_frame = ctk.CTkFrame(self)
        top_frame.pack(fill="x", padx=10, pady=10)

        # 标题
        title_label = ctk.CTkLabel(
            top_frame,
            text="📁 文档全文搜索",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=5)

        # ===== 目录选择区域 =====
        dir_frame = ctk.CTkFrame(self)
        dir_frame.pack(fill="x", padx=10, pady=5)

        self.dir_label = ctk.CTkLabel(
            dir_frame,
            text="未选择目录",
            font=ctk.CTkFont(size=12)
        )
        self.dir_label.pack(side="left", padx=10, pady=10)

        select_dir_btn = ctk.CTkButton(
            dir_frame,
            text="选择目录",
            command=self._select_directory,
            width=120
        )
        select_dir_btn.pack(side="right", padx=10, pady=10)

        sync_btn = ctk.CTkButton(
            dir_frame,
            text="🔄 智能同步",
            command=self._smart_sync,
            width=120,
            fg_color="orange",
            hover_color="darkorange"
        )
        sync_btn.pack(side="right", padx=5, pady=10)

        index_btn = ctk.CTkButton(
            dir_frame,
            text="开始索引",
            command=self._start_indexing,
            width=120,
            fg_color="green",
            hover_color="darkgreen"
        )
        index_btn.pack(side="right", padx=5, pady=10)

        clear_btn = ctk.CTkButton(
            dir_frame,
            text="清空索引",
            command=self._clear_index,
            width=120,
            fg_color="red",
            hover_color="darkred"
        )
        clear_btn.pack(side="right", padx=5, pady=10)

        # ===== 搜索区域 =====
        search_frame = ctk.CTkFrame(self)
        search_frame.pack(fill="x", padx=10, pady=5)

        # 搜索框
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="输入搜索关键词...",
            font=ctk.CTkFont(size=14),
            height=40
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        self.search_entry.bind("<Return>", lambda e: self._perform_search())

        # 搜索类型选择
        self.search_type = ctk.StringVar(value="content")
        search_type_menu = ctk.CTkSegmentedButton(
            search_frame,
            values=["内容搜索", "文件名搜索"],
            variable=self.search_type,
            command=self._on_search_type_changed,
            width=200
        )
        search_type_menu.pack(side="left", padx=5, pady=10)

        # 搜索按钮
        search_btn = ctk.CTkButton(
            search_frame,
            text="🔍 搜索",
            command=self._perform_search,
            width=100,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        search_btn.pack(side="left", padx=10, pady=10)

        # ===== 进度条 =====
        self.progress_frame = ctk.CTkFrame(self)
        self.progress_frame.pack(fill="x", padx=10, pady=5)

        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            text="就绪",
            font=ctk.CTkFont(size=11)
        )
        self.progress_label.pack(side="left", padx=10, pady=5)

        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.pack(side="left", fill="x", expand=True, padx=10, pady=5)
        self.progress_bar.set(0)

        # ===== 统计信息 =====
        stats_frame = ctk.CTkFrame(self)
        stats_frame.pack(fill="x", padx=10, pady=5)

        self.stats_label = ctk.CTkLabel(
            stats_frame,
            text="索引文档: 0 | 索引大小: 0 KB",
            font=ctk.CTkFont(size=11)
        )
        self.stats_label.pack(padx=10, pady=5)

        # ===== 结果显示区域 =====
        results_frame = ctk.CTkFrame(self)
        results_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # 结果标签
        self.results_label = ctk.CTkLabel(
            results_frame,
            text="搜索结果 (0)",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.results_label.pack(anchor="w", padx=10, pady=5)

        # 结果列表（使用文本框模拟）
        self.results_text = ctk.CTkTextbox(
            results_frame,
            font=ctk.CTkFont(size=12),
            wrap="none"
        )
        self.results_text.pack(fill="both", expand=True, padx=10, pady=5)

        # ===== 底部状态栏 =====
        status_frame = ctk.CTkFrame(self)
        status_frame.pack(fill="x", padx=10, pady=5)

        self.status_label = ctk.CTkLabel(
            status_frame,
            text="准备就绪",
            font=ctk.CTkFont(size=10)
        )
        self.status_label.pack(side="left", padx=10, pady=5)

    def _on_search_type_changed(self, value):
        """搜索类型改变事件"""
        if value == "内容搜索":
            self.search_type.set("content")
        else:
            self.search_type.set("filename")

    def _select_directory(self):
        """选择要索引的目录"""
        directory = filedialog.askdirectory(title="选择要索引的目录")

        if directory:
            self.current_directory = directory
            self.dir_label.configure(text=f"📂 {directory}")
            self.status_label.configure(text=f"已选择目录: {directory}")
            logger.info(f"选择目录: {directory}")

    def _start_indexing(self):
        """开始索引"""
        if not self.current_directory:
            messagebox.showwarning("警告", "请先选择要索引的目录")
            return

        if self.indexing_thread and self.indexing_thread.is_alive():
            messagebox.showinfo("提示", "索引正在进行中...")
            return

        # 在后台线程执行索引
        self.indexing_thread = threading.Thread(target=self._index_worker, daemon=True)
        self.indexing_thread.start()

    def _index_worker(self):
        """索引工作线程"""
        try:
            self.progress_bar.set(0)
            self.progress_label.configure(text="索引中...")

            def progress_callback(current, total, filename):
                """进度回调"""
                progress = current / total if total > 0 else 0
                self.progress_bar.set(progress)
                self.progress_label.configure(
                    text=f"索引中: {current}/{total} - {Path(filename).name}"
                )

            # 执行索引
            stats = self.search_engine.index_directory(
                self.current_directory,
                progress_callback
            )

            # 更新统计
            self._update_stats()

            # 完成
            self.progress_bar.set(1.0)
            self.progress_label.configure(
                text=f"索引完成! 成功: {stats['indexed']}, 错误: {stats['errors']}"
            )
            self.status_label.configure(
                text=f"索引完成: {stats['indexed']} 个文件"
            )

            messagebox.showinfo(
                "索引完成",
                f"成功索引 {stats['indexed']} 个文件\n"
                f"内容索引: {stats['content_indexed']}\n"
                f"文件名索引: {stats['filename_only']}\n"
                f"错误: {stats['errors']}"
            )

        except Exception as e:
            logger.error(f"索引失败: {e}")
            messagebox.showerror("错误", f"索引失败: {e}")
            self.progress_label.configure(text="索引失败")

    def _smart_sync(self):
        """智能同步 - 检测文件变化并增量更新索引"""
        if not self.current_directory:
            messagebox.showwarning("警告", "请先选择要索引的目录")
            return

        if self.indexing_thread and self.indexing_thread.is_alive():
            messagebox.showinfo("提示", "索引正在进行中...")
            return

        # 在后台线程执行同步
        self.indexing_thread = threading.Thread(target=self._sync_worker, daemon=True)
        self.indexing_thread.start()

    def _sync_worker(self):
        """同步工作线程"""
        try:
            self.progress_bar.set(0)
            self.progress_label.configure(text="检测文件变化...")

            def progress_callback(current, total, description):
                """进度回调"""
                progress = current / total if total > 0 else 0
                self.progress_bar.set(progress)
                self.progress_label.configure(text=f"同步中: {current}/{total} - {description}")

            # 执行同步
            stats = self.search_engine.sync_directory(
                self.current_directory,
                progress_callback
            )

            # 更新统计
            self._update_stats()

            # 完成
            self.progress_bar.set(1.0)

            # 显示结果
            if stats['added'] == 0 and stats['updated'] == 0 and stats['deleted'] == 0:
                self.progress_label.configure(text="没有文件变化")
                self.status_label.configure(text="索引已是最新")
                messagebox.showinfo("同步完成", "没有检测到文件变化，索引已是最新！")
            else:
                self.progress_label.configure(
                    text=f"同步完成! 新增: {stats['added']}, 更新: {stats['updated']}, 删除: {stats['deleted']}"
                )
                self.status_label.configure(text=f"同步完成: 处理了 {stats['added'] + stats['updated'] + stats['deleted']} 个变化")

                messagebox.showinfo(
                    "同步完成",
                    f"✅ 扫描文件: {stats['scanned']} 个\n"
                    f"📄 新增: {stats['added']} 个\n"
                    f"🔄 更新: {stats['updated']} 个\n"
                    f"🗑️ 删除: {stats['deleted']} 个\n"
                    f"✔️ 未变化: {stats['unchanged']} 个\n"
                    f"❌ 错误: {stats['errors']} 个"
                )

        except Exception as e:
            logger.error(f"同步失败: {e}")
            messagebox.showerror("错误", f"同步失败: {e}")
            self.progress_label.configure(text="同步失败")

    def _perform_search(self):
        """执行搜索"""
        query = self.search_entry.get().strip()

        if not query:
            messagebox.showwarning("警告", "请输入搜索关键词")
            return

        # 确定搜索类型
        search_type = "content" if self.search_type.get() == "content" else "filename"

        self.status_label.configure(text=f"搜索中: {query}")

        try:
            # 执行搜索
            results = self.search_engine.search(query, search_type=search_type)

            # 显示结果
            self._display_results(results, query)

            self.status_label.configure(
                text=f"找到 {len(results)} 个结果"
            )

        except Exception as e:
            logger.error(f"搜索失败: {e}")
            messagebox.showerror("错误", f"搜索失败: {e}")

    def _display_results(self, results, query):
        """显示搜索结果"""
        self.results_text.delete("1.0", "end")
        self.results_label.configure(text=f"搜索结果 ({len(results)})")

        if not results:
            self.results_text.insert("1.0", "未找到匹配的文件")
            return

        # 格式化显示结果
        for idx, result in enumerate(results, 1):
            path = result['path']
            filename = result['filename']
            size = result['size']
            modified = result.get('modified', '')
            has_content = result.get('has_content', False)
            score = result.get('score', 0)

            # 格式化大小
            size_str = self._format_size(size)

            # 格式化时间
            time_str = modified.strftime('%Y-%m-%d %H:%M') if modified else 'N/A'

            # 内容标记
            content_mark = "📄" if has_content else "📁"

            # 插入结果
            result_text = (
                f"{idx}. {content_mark} {filename}\n"
                f"   路径: {path}\n"
                f"   大小: {size_str} | 修改时间: {time_str} | 相关度: {score:.2f}\n"
                f"{'-' * 80}\n"
            )

            self.results_text.insert("end", result_text)

        # 支持双击打开文件
        self.results_text.bind("<Double-Button-1>", self._open_file_from_results)

    def _open_file_from_results(self, event):
        """从结果中打开文件"""
        try:
            # 获取当前行
            current_line = self.results_text.get("insert linestart", "insert lineend")

            # 提取路径
            if "路径:" in current_line:
                path = current_line.split("路径:")[1].strip()
                if os.path.exists(path):
                    os.startfile(path) if os.name == 'nt' else os.system(f'xdg-open "{path}"')
                    logger.info(f"打开文件: {path}")

        except Exception as e:
            logger.error(f"打开文件失败: {e}")

    def _clear_index(self):
        """清空索引"""
        result = messagebox.askyesno("确认", "确定要清空所有索引吗？")

        if result:
            try:
                self.search_engine.clear_index()
                self._update_stats()
                self.results_text.delete("1.0", "end")
                self.results_label.configure(text="搜索结果 (0)")
                self.status_label.configure(text="索引已清空")
                messagebox.showinfo("成功", "索引已清空")
            except Exception as e:
                logger.error(f"清空索引失败: {e}")
                messagebox.showerror("错误", f"清空索引失败: {e}")

    def _update_stats(self):
        """更新统计信息"""
        try:
            stats = self.search_engine.get_stats()
            total_docs = stats.get('total_documents', 0)
            index_size = stats.get('index_size', 0)

            size_str = self._format_size(index_size)

            self.stats_label.configure(
                text=f"索引文档: {total_docs} | 索引大小: {size_str}"
            )
        except Exception as e:
            logger.error(f"更新统计信息失败: {e}")

    def _check_sync_on_startup(self):
        """启动时检查是否需要同步"""
        try:
            stats = self.search_engine.get_stats()
            total_docs = stats.get('total_documents', 0)

            # 如果已有索引，获取索引中的第一个文件路径作为参考
            if total_docs > 0:
                # 尝试从索引中获取一个目录路径
                with self.search_engine.ix.searcher() as searcher:
                    for doc in searcher.all_stored_fields():
                        path = doc.get('path')
                        if path and os.path.exists(path):
                            # 提取目录路径
                            directory = str(Path(path).parent)

                            # 找到根目录（向上查找直到找到包含多个索引文件的目录）
                            while directory and directory != os.path.dirname(directory):
                                # 检查这个目录下有多少文件在索引中
                                count = 0
                                with self.search_engine.ix.searcher() as s2:
                                    for d in s2.all_stored_fields():
                                        if d.get('path', '').startswith(directory):
                                            count += 1
                                            if count > 5:  # 如果找到超过5个文件，认为这是根目录
                                                break

                                if count > 5:
                                    break

                                directory = os.path.dirname(directory)

                            # 设置为当前目录
                            self.current_directory = directory
                            self.dir_label.configure(text=f"📂 {directory}")

                            # 提示用户是否同步
                            response = messagebox.askyesno(
                                "检测到现有索引",
                                f"发现已索引 {total_docs} 个文件。\n\n"
                                f"目录: {directory}\n\n"
                                "是否检查文件变化并同步索引？\n\n"
                                "（推荐：如果文件有更新，选择"是"）",
                                icon='question'
                            )

                            if response:
                                # 用户选择同步
                                self._smart_sync()

                            break

        except Exception as e:
            logger.error(f"启动检查失败: {e}")

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"


def run_app():
    """运行应用"""
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_app()
