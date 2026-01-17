"""
打包脚本 - 使用 PyInstaller 打包成独立应用
"""

import os
import sys
import shutil
import subprocess


def clean_build():
    """清理构建目录"""
    dirs_to_clean = ['build', 'dist', '__pycache__']

    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"清理目录: {dir_name}")
            shutil.rmtree(dir_name, ignore_errors=True)

    # 清理 .spec 文件
    for file in os.listdir('.'):
        if file.endswith('.spec'):
            print(f"删除文件: {file}")
            os.remove(file)


def build_app():
    """构建应用"""
    print("=" * 50)
    print("开始打包 FileSearch 应用")
    print("=" * 50)

    # PyInstaller 命令
    command = [
        'pyinstaller',
        '--name=FileSearch',
        '--onefile',  # 打包成单个文件
        '--windowed',  # 不显示控制台窗口
        '--icon=NONE',  # 如果有图标，可以指定路径
        '--add-data=src:src',  # 添加源代码目录
        'main.py'
    ]

    # Windows 平台特殊处理
    if sys.platform == 'win32':
        command.insert(-1, '--add-data=src;src')
    else:
        command.insert(-1, '--add-data=src:src')

    print(f"\n执行命令: {' '.join(command)}\n")

    try:
        subprocess.run(command, check=True)

        print("\n" + "=" * 50)
        print("✅ 打包完成！")
        print("=" * 50)
        print(f"\n可执行文件位置: {os.path.abspath('dist/FileSearch')}")
        print("\n注意事项:")
        print("1. 首次运行需要选择目录并创建索引")
        print("2. index 目录会在应用同级目录下自动创建")
        print("3. 建议将应用放在固定位置使用\n")

    except subprocess.CalledProcessError as e:
        print(f"\n❌ 打包失败: {e}")
        sys.exit(1)


def main():
    """主函数"""
    print("FileSearch 打包工具\n")

    # 检查是否安装了 PyInstaller
    try:
        import PyInstaller
    except ImportError:
        print("❌ PyInstaller 未安装")
        print("\n请先安装 PyInstaller:")
        print("  pip install pyinstaller\n")
        sys.exit(1)

    # 清理旧的构建
    clean_build()

    # 构建应用
    build_app()


if __name__ == "__main__":
    main()
