#!/bin/bash

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt

# 检查环境变量文件
if [ ! -f ".env" ]; then
    echo "请创建 .env 文件并设置必要的环境变量"
    echo "ZHIPUAI_API_KEY=your_api_key_here" > .env
    exit 1
fi

# 创建必要的目录
mkdir -p exports
mkdir -p vector_store
mkdir -p templates

# 启动程序
echo "启动智能助手..."
if [ "$1" == "--web" ]; then
    echo "启动Web界面模式..."
    python3 main.py --web
elif [ "$1" == "--voice" ]; then
    echo "启动语音交互模式..."
    python3 main.py --voice
else
    echo "启动命令行模式..."
    python3 main.py
fi
