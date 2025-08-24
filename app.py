#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LaOpen 主应用文件
像素风格的网站项目，具有完整的网球管理系统
"""

from flask import Flask
from flask_login import LoginManager
import os

# 导入自定义模块
from models import db, init_db
from auth import auth_bp, init_auth
from main import main_bp

def create_app():
    """应用工厂函数"""
    app = Flask(__name__)
    
    # 应用配置
    # 生产环境从环境变量读取，开发环境使用默认值
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'laopen-secret-key-2024')
    
    # 数据库配置
    basedir = os.path.abspath(os.path.dirname(__file__))
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # 确保instance目录存在
        instance_dir = os.path.join(basedir, 'instance')
        os.makedirs(instance_dir, exist_ok=True)
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{basedir}/instance/laopen.db'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = os.environ.get('FLASK_ENV') != 'production'
    
    # 初始化数据库
    db.init_app(app)
    
    # 初始化登录管理器
    login_manager = LoginManager()
    login_manager.init_app(app)
    init_auth(login_manager)
    
    # 注册蓝图
    from tennis import tennis_bp
    from match_management import match_mgmt_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(tennis_bp)
    app.register_blueprint(match_mgmt_bp)
    
    return app

def init_directories():
    """创建必要的目录"""
    directories = ['templates', 'static/css', 'static/js', 'instance']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ 目录创建成功：{directory}")

if __name__ == '__main__':
    # 创建必要的目录
    init_directories()
    
    # 创建应用实例
    app = create_app()
    
    # 初始化数据库
    print("🚀 正在初始化数据库...")
    if init_db(app):
        # 读取环境变量
        port = int(os.environ.get('PORT', 5000))
        debug = os.environ.get('FLASK_ENV') != 'production'
        
        if debug:
            print("🎉 开发环境启动成功！")
            print(f"📱 请在浏览器中访问：http://localhost:{port}")
            print("⚡ 按 Ctrl+C 停止服务器")
        else:
            print("🎉 生产环境启动成功！")
            print(f"🌍 应用运行在端口：{port}")
        
        print("=" * 50)
        app.run(debug=debug, host='0.0.0.0', port=port)
    else:
        print("❌ 应用启动失败，请检查数据库配置")
        print("💡 提示：运行 python3 create_test_data.py 来创建测试数据")
