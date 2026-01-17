"""
文档内容提取模块
支持 PDF, DOCX, DOC, MD, TXT 等格式
"""

import os
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class DocumentParser:
    """文档内容解析器"""

    # 支持内容提取的文件扩展名
    CONTENT_EXTRACTABLE_EXTENSIONS = {'.pdf', '.docx', '.doc', '.md', '.txt'}

    # 视频和音频文件扩展名（仅索引文件名）
    MEDIA_EXTENSIONS = {
        # 视频
        '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg',
        # 音频
        '.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', '.opus'
    }

    @staticmethod
    def can_extract_content(file_path: str) -> bool:
        """判断文件是否支持内容提取"""
        ext = Path(file_path).suffix.lower()
        return ext in DocumentParser.CONTENT_EXTRACTABLE_EXTENSIONS

    @staticmethod
    def is_media_file(file_path: str) -> bool:
        """判断是否为视频或音频文件"""
        ext = Path(file_path).suffix.lower()
        return ext in DocumentParser.MEDIA_EXTENSIONS

    @staticmethod
    def extract_text(file_path: str) -> Optional[str]:
        """
        提取文档内容

        Args:
            file_path: 文件路径

        Returns:
            提取的文本内容，失败返回 None
        """
        if not os.path.exists(file_path):
            logger.error(f"文件不存在: {file_path}")
            return None

        ext = Path(file_path).suffix.lower()

        try:
            if ext == '.pdf':
                return DocumentParser._extract_pdf(file_path)
            elif ext == '.docx':
                return DocumentParser._extract_docx(file_path)
            elif ext == '.doc':
                return DocumentParser._extract_doc(file_path)
            elif ext in {'.md', '.txt'}:
                return DocumentParser._extract_text_file(file_path)
            else:
                logger.warning(f"不支持的文件格式: {ext}")
                return None
        except Exception as e:
            logger.error(f"提取文件内容失败 {file_path}: {e}")
            return None

    @staticmethod
    def _extract_pdf(file_path: str) -> str:
        """提取 PDF 内容"""
        try:
            import fitz  # PyMuPDF

            text = []
            with fitz.open(file_path) as doc:
                for page in doc:
                    text.append(page.get_text())

            return '\n'.join(text)
        except ImportError:
            logger.error("PyMuPDF 未安装，无法解析 PDF 文件")
            return ""
        except Exception as e:
            logger.error(f"PDF 解析失败: {e}")
            return ""

    @staticmethod
    def _extract_docx(file_path: str) -> str:
        """提取 DOCX 内容"""
        try:
            from docx import Document

            doc = Document(file_path)
            text = []

            # 提取段落
            for para in doc.paragraphs:
                if para.text.strip():
                    text.append(para.text)

            # 提取表格
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        if cell.text.strip():
                            text.append(cell.text)

            return '\n'.join(text)
        except ImportError:
            logger.error("python-docx 未安装，无法解析 DOCX 文件")
            return ""
        except Exception as e:
            logger.error(f"DOCX 解析失败: {e}")
            return ""

    @staticmethod
    def _extract_doc(file_path: str) -> str:
        """
        提取 DOC 内容（旧版 Word 格式）

        Windows: 使用 pywin32
        Linux/Mac: 尝试使用 antiword 或返回空
        """
        import platform

        if platform.system() == 'Windows':
            try:
                import win32com.client

                word = win32com.client.Dispatch("Word.Application")
                word.Visible = False

                try:
                    doc = word.Documents.Open(os.path.abspath(file_path))
                    text = doc.Content.Text
                    doc.Close()
                    return text
                finally:
                    word.Quit()
            except ImportError:
                logger.error("pywin32 未安装，无法解析 DOC 文件")
                return ""
            except Exception as e:
                logger.error(f"DOC 解析失败: {e}")
                return ""
        else:
            # Linux/Mac: 尝试使用 antiword
            try:
                import subprocess
                result = subprocess.run(
                    ['antiword', file_path],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    return result.stdout
                else:
                    logger.warning(f"antiword 解析失败，请安装 antiword")
                    return ""
            except FileNotFoundError:
                logger.warning("antiword 未安装，跳过 DOC 文件解析")
                return ""
            except Exception as e:
                logger.error(f"DOC 解析失败: {e}")
                return ""

    @staticmethod
    def _extract_text_file(file_path: str) -> str:
        """提取纯文本和 Markdown 内容"""
        encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']

        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
            except Exception as e:
                logger.error(f"读取文件失败 {file_path}: {e}")
                return ""

        logger.warning(f"无法识别文件编码: {file_path}")
        return ""


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)

    parser = DocumentParser()
    test_file = "test.txt"

    if os.path.exists(test_file):
        content = parser.extract_text(test_file)
        print(f"提取内容: {content[:200]}...")
