"""
FileSearch 安装配置
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="filesearch",
    version="1.0.0",
    author="FileSearch Team",
    description="一个轻量级的文档全文搜索工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/filesearch",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Desktop Environment :: File Managers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "customtkinter>=5.2.2",
        "whoosh>=2.7.4",
        "PyMuPDF>=1.23.26",
        "python-docx>=1.1.0",
        "watchdog>=4.0.0",
        "pillow>=10.2.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pyinstaller>=5.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "filesearch=main:main",
        ],
    },
)
