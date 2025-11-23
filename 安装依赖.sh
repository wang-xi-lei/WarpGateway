#!/bin/bash
# WarpGateway Mac 依赖安装脚本

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 python3，请先安装 Python 3.8+"
    echo "   可以使用 Homebrew: brew install python3"
    exit 1
fi

# 虚拟环境目录
VENV_DIR=".venv"

echo "🔧 设置 WarpGateway 环境..."

# 创建虚拟环境
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo "❌ 虚拟环境创建失败"
        exit 1
    fi
    echo "✅ 虚拟环境创建成功"
else
    echo "✅ 虚拟环境已存在"
fi

# 激活虚拟环境
echo "📦 激活虚拟环境..."
source "$VENV_DIR/bin/activate"

# 升级 pip
echo "⬆️  升级 pip..."
pip install --upgrade pip

# 安装依赖
echo "📦 安装项目依赖..."
pip install -e .

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 依赖安装完成！"
    echo ""
    echo "现在可以运行："
    echo "  ./启动WarpGateway.sh    # 启动 GUI"
    echo "  或"
    echo "  source .venv/bin/activate && python run_gui.py"
else
    echo "❌ 依赖安装失败"
    exit 1
fi

