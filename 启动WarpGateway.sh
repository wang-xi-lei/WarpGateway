#!/bin/bash
# WarpGateway Mac 启动脚本

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 python3，请先安装 Python 3.8+"
    exit 1
fi

# 虚拟环境目录
VENV_DIR=".venv"

# 检查虚拟环境是否存在
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo "❌ 虚拟环境创建失败"
        exit 1
    fi
fi

# 激活虚拟环境
echo "📦 激活虚拟环境..."
source "$VENV_DIR/bin/activate"

# 检查依赖
if ! python -c "import mitmproxy, yaml, PySide6" 2>/dev/null; then
    echo "📦 检测到缺少依赖，正在安装..."
    pip install -e .
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败"
        exit 1
    fi
    echo "✅ 依赖安装完成"
fi

# 启动 GUI
echo "🚀 启动 WarpGateway..."
python run_gui.py

