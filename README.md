# 📁 FileSearch - 文档全文搜索工具

一个轻量级的桌面应用，支持对文档内容和文件名进行全文索引和快速搜索。

## ✨ 功能特性

- 🔍 **全文搜索**: 支持 PDF, DOCX, DOC, MD, TXT 文档内容搜索
- 📝 **文件名搜索**: 支持所有文件类型（包括视频、音频）的文件名搜索
- ⚡ **快速索引**: 基于 Whoosh 搜索引擎，毫秒级响应
- 🎨 **现代化界面**: 使用 CustomTkinter 构建美观的用户界面
- 🔄 **智能同步**: 程序重启时自动检测文件变化（新增/修改/删除），增量更新索引
- 📊 **启动检测**: 自动识别已有索引，提示是否同步更新
- 💾 **轻量级**: 打包后仅 5-10MB

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行应用

```bash
python main.py
```

## 📦 支持的文件格式

### 内容索引
- PDF (.pdf)
- Word 文档 (.docx, .doc)
- Markdown (.md)
- 文本文件 (.txt)

### 文件名索引
- 所有文件类型（视频、音频、图片等）

## 🏗️ 项目结构

```
FileSearch358/
├── main.py                    # 应用入口
├── requirements.txt           # 依赖配置
├── src/
│   ├── ui/
│   │   └── main_window.py    # CustomTkinter UI
│   ├── indexer/
│   │   ├── document_parser.py  # 文档内容提取
│   │   └── search_engine.py    # Whoosh 搜索引擎
│   └── utils/
│       └── file_watcher.py     # 文件监控
└── index/                     # 索引存储目录
```

## 🛠️ 技术栈

- **UI 框架**: CustomTkinter 5.2
- **搜索引擎**: Whoosh 2.7
- **PDF 解析**: PyMuPDF
- **DOCX 解析**: python-docx
- **文件监控**: watchdog

## 📖 使用说明

1. 启动应用后，点击"选择目录"按钮
2. 选择要索引的文件夹
3. 等待索引完成（进度条显示）
4. 在搜索框输入关键词
5. 选择搜索类型（内容/文件名）
6. 查看搜索结果

## 📄 License

MIT License
