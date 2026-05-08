#!/bin/zsh
# 动物习作AI智能助教 - 启动脚本
# 双击此文件即可启动应用

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "  动物习作AI智能助教 启动中..."
echo "========================================"
echo ""

# 检查Python是否可用
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未检测到Python环境"
    echo "请安装Python 3后重试"
    echo "下载地址：https://www.python.org/downloads/"
    echo ""
    read -p "按回车键退出..."
    exit 1
fi

# 检查依赖是否安装
python3 -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 正在安装依赖（首次运行需要安装）..."
    pip3 install flask openai 2>&1 | tail -1
    echo ""
fi

echo "🌐 正在启动本地服务..."
echo ""
echo "📖 请在浏览器中打开以下地址："
echo "  http://127.0.0.1:5001"
echo ""
echo "💡 提示：启动后会自动打开浏览器"
echo ""

# 尝试自动打开浏览器
sleep 2 && open "http://127.0.0.1:5001" 2>/dev/null &

# 启动Flask应用
python3 app.py

echo ""
echo "服务已停止。"
read -p "按回车键退出..."
