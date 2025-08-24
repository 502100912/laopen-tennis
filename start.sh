#!/bin/bash

# LaOpen 项目启动脚本

echo "🚀 正在启动 LaOpen 项目..."
echo "=" * 50

# 检查 Python3 是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：Python3 未安装"
    echo "💡 请先安装 Python 3.7 或更高版本"
    exit 1
fi

# SQLite 无需额外服务
echo "💎 使用 SQLite 数据库 - 零配置，开箱即用！"

# 检查是否安装了核心依赖
echo "🔍 检查依赖包..."
if ! python3 -c "import flask" &> /dev/null; then
    echo "📦 正在安装依赖包..."
    python3 -m pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败"
        exit 1
    fi
    echo "✅ 依赖安装完成"
fi

# 检查SQLite数据库
echo "🗄️  检查SQLite数据库..."
if python3 -c "
import sqlite3
import os
try:
    # 确保instance目录存在
    os.makedirs('instance', exist_ok=True)
    if not os.path.exists('instance/laopen.db'):
        print('💡 数据库文件不存在，将自动创建')
        conn = sqlite3.connect('instance/laopen.db')
        conn.close()
    else:
        conn = sqlite3.connect('instance/laopen.db')
        conn.close()
    print('✅ SQLite数据库就绪')
except Exception as e:
    print(f'❌ SQLite数据库错误: {e}')
    exit(1)
" 2>/dev/null; then
    echo "✅ 数据库检查通过"
else
    echo "❌ 数据库检查失败"
    exit 1
fi

# 检查端口5000是否被占用
echo "🔍 检查端口5000状态..."
if lsof -ti:5000 > /dev/null 2>&1; then
    echo "⚠️  端口5000被占用，正在处理..."
    
    # 获取占用端口的进程信息
    PROCESS_INFO=$(lsof -i:5000 | grep LISTEN)
    echo "📋 占用进程信息: $PROCESS_INFO"
    
    # 获取进程PID并尝试杀死
    PID=$(lsof -ti:5000)
    if [ ! -z "$PID" ]; then
        echo "🔪 正在终止进程 PID: $PID"
        kill -TERM $PID 2>/dev/null
        
        # 等待2秒让进程正常退出
        sleep 2
        
        # 如果进程还在运行，强制杀死
        if kill -0 $PID 2>/dev/null; then
            echo "💀 强制终止进程 PID: $PID"
            kill -KILL $PID 2>/dev/null
        fi
        
        # 再次检查端口是否可用
        sleep 1
        if lsof -ti:5000 > /dev/null 2>&1; then
            echo "❌ 无法释放端口5000，请手动检查"
            echo "💡 试运行: lsof -i:5000"
            exit 1
        else
            echo "✅ 端口5000已释放"
        fi
    fi
else
    echo "✅ 端口5000可用"
fi

# 启动应用
echo "⚡ 启动 Flask 应用..."
echo "🌐 访问地址: http://localhost:5000"
echo "🛑 按 Ctrl+C 停止服务器"
echo "=" * 50

python3 app.py
