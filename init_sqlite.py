#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LaOpen SQLite数据库初始化脚本
简单的数据库初始化，无需安装额外服务
"""

import os
import sqlite3
import sys

def init_sqlite_db():
    """初始化SQLite数据库"""
    # 确保instance目录存在
    os.makedirs('instance', exist_ok=True)
    db_path = 'instance/laopen.db'
    
    try:
        # 检查数据库文件是否存在
        if os.path.exists(db_path):
            print(f"✅ SQLite数据库已存在：{db_path}")
        else:
            # 创建数据库文件（通过连接自动创建）
            conn = sqlite3.connect(db_path)
            conn.close()
            print(f"✅ SQLite数据库创建成功：{db_path}")
        
        # 测试连接
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT sqlite_version()")
        version = cursor.fetchone()[0]
        conn.close()
        
        print(f"✅ SQLite版本：{version}")
        print(f"✅ 数据库路径：{os.path.abspath(db_path)}")
        
        return True
        
    except Exception as e:
        print(f"❌ SQLite数据库初始化失败：{e}")
        return False

def check_db_size():
    """检查数据库大小"""
    db_path = 'instance/laopen.db'
    if os.path.exists(db_path):
        size = os.path.getsize(db_path)
        if size < 1024:
            print(f"📊 数据库大小：{size} bytes")
        elif size < 1024 * 1024:
            print(f"📊 数据库大小：{size/1024:.1f} KB")
        else:
            print(f"📊 数据库大小：{size/(1024*1024):.1f} MB")

if __name__ == '__main__':
    print("🚀 LaOpen SQLite数据库初始化开始...")
    print("=" * 50)
    
    if init_sqlite_db():
        check_db_size()
        print("=" * 50)
        print("🎉 SQLite数据库初始化完成！")
        print("现在可以运行以下命令启动应用：")
        print("  python3 app.py")
        print("  或者：./start.sh")
        print("")
        print("💡 SQLite优势：")
        print("  • 零配置，无需安装数据库服务器")
        print("  • 数据存储在单个文件中")
        print("  • 支持完整的SQL功能")
        print("  • 适合开发和小型项目")
    else:
        sys.exit(1)
