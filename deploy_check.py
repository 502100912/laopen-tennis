#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LaOpen 部署检查脚本
检查应用是否准备好部署到生产环境
"""

import os
import sys
import subprocess
from pathlib import Path

def check_files():
    """检查必要的部署文件"""
    print("📁 检查部署文件...")
    
    required_files = [
        'app.py',
        'requirements.txt', 
        'Procfile',
        'models.py',
        'templates/',
        'static/',
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"  ✅ {file_path}")
    
    if missing_files:
        print(f"  ❌ 缺少文件: {', '.join(missing_files)}")
        return False
    
    print("  🎉 所有必要文件都存在")
    return True

def check_requirements():
    """检查依赖文件"""
    print("\n📦 检查Python依赖...")
    
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read().strip().split('\n')
        
        essential_packages = [
            'Flask',
            'Flask-SQLAlchemy', 
            'Flask-Login',
            'Flask-WTF',
            'bcrypt'
        ]
        
        found_packages = []
        for req in requirements:
            package_name = req.split('>=')[0].split('==')[0]
            if package_name in essential_packages:
                found_packages.append(package_name)
                print(f"  ✅ {req}")
        
        missing_packages = set(essential_packages) - set(found_packages)
        if missing_packages:
            print(f"  ❌ 缺少依赖: {', '.join(missing_packages)}")
            return False
        
        print("  🎉 所有必要依赖都存在")
        return True
        
    except FileNotFoundError:
        print("  ❌ requirements.txt 文件不存在")
        return False

def check_git_status():
    """检查Git状态"""
    print("\n🔧 检查Git状态...")
    
    try:
        # 检查是否有未提交的更改
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, check=True)
        
        if result.stdout.strip():
            print("  ⚠️  有未提交的更改:")
            print(f"     {result.stdout.strip()}")
            print("  💡 建议先提交并推送到GitHub")
            return False
        else:
            print("  ✅ 所有更改已提交")
            
        # 检查远程仓库
        result = subprocess.run(['git', 'remote', '-v'], 
                              capture_output=True, text=True, check=True)
        if 'github.com' in result.stdout:
            print("  ✅ GitHub仓库已配置")
            return True
        else:
            print("  ⚠️  未检测到GitHub仓库")
            print("  💡 需要推送到GitHub进行部署")
            return False
            
    except subprocess.CalledProcessError:
        print("  ❌ 不是Git仓库或Git命令失败")
        print("  💡 需要初始化Git并推送到GitHub")
        return False
    except FileNotFoundError:
        print("  ❌ 未安装Git")
        return False

def test_app_locally():
    """测试应用本地运行"""
    print("\n🧪 测试应用本地运行...")
    
    try:
        from app import create_app
        app = create_app()
        
        # 测试应用创建
        print("  ✅ 应用创建成功")
        
        # 测试配置
        if app.config.get('SECRET_KEY'):
            print("  ✅ SECRET_KEY已配置")
        else:
            print("  ❌ SECRET_KEY未配置")
            
        # 测试数据库配置
        if app.config.get('SQLALCHEMY_DATABASE_URI'):
            print("  ✅ 数据库URI已配置")
        else:
            print("  ❌ 数据库URI未配置")
            
        return True
        
    except Exception as e:
        print(f"  ❌ 应用测试失败: {e}")
        return False

def generate_env_template():
    """生成环境变量模板"""
    print("\n📝 生成环境变量模板...")
    
    env_template = """# LaOpen 生产环境变量配置模板
# 在部署平台中设置这些环境变量

# 必需的环境变量
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here-make-it-very-strong

# 可选的环境变量
DATABASE_URL=sqlite:///instance/laopen.db
PORT=5000

# 部署平台会自动设置的变量
# PORT (Render, Heroku等会自动设置)
# DATABASE_URL (如果使用平台提供的数据库)
"""
    
    with open('.env.template', 'w') as f:
        f.write(env_template)
    
    print("  ✅ 已创建 .env.template 文件")
    print("  💡 将此模板中的值设置为环境变量")

def show_deployment_instructions():
    """显示部署指令"""
    print("\n🚀 部署指令:")
    print("="*50)
    
    print("\n1️⃣  最快部署 - Render.com (推荐):")
    print("   • 访问 https://render.com")
    print("   • 登录并连接GitHub")
    print("   • 创建 Web Service")
    print("   • 选择你的仓库")
    print("   • 配置:")
    print("     - Build Command: pip install -r requirements.txt")
    print("     - Start Command: python app.py")
    print("     - 设置环境变量 FLASK_ENV=production")
    
    print("\n2️⃣  备选方案 - Railway.app:")
    print("   • 访问 https://railway.app") 
    print("   • 连接GitHub仓库")
    print("   • 自动检测并部署")
    
    print("\n3️⃣  其他选项:")
    print("   • PythonAnywhere (免费tier)")
    print("   • Heroku (付费但稳定)")
    print("   • DigitalOcean App Platform")
    
    print(f"\n📖 详细指南请查看: DEPLOY.md")

def main():
    """主检查流程"""
    print("🎾 LaOpen 部署准备检查")
    print("="*50)
    
    checks = [
        ("文件检查", check_files),
        ("依赖检查", check_requirements), 
        ("Git状态", check_git_status),
        ("应用测试", test_app_locally),
    ]
    
    passed_checks = 0
    total_checks = len(checks)
    
    for check_name, check_func in checks:
        try:
            if check_func():
                passed_checks += 1
        except Exception as e:
            print(f"  ❌ {check_name}检查出错: {e}")
    
    # 生成环境变量模板
    generate_env_template()
    
    print(f"\n📊 检查结果: {passed_checks}/{total_checks} 通过")
    
    if passed_checks == total_checks:
        print("🎉 所有检查通过！应用已准备好部署")
        show_deployment_instructions()
        return True
    else:
        failed_checks = total_checks - passed_checks
        print(f"⚠️  有 {failed_checks} 项检查未通过，请修复后再部署")
        
        # 给出修复建议
        print("\n🔧 修复建议:")
        if not Path('Procfile').exists():
            print("  • 创建 Procfile 文件")
        
        # 检查Git状态
        try:
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, check=True)
            if result.stdout.strip():
                print("  • 提交并推送所有更改到GitHub:")
                print("    git add .")
                print("    git commit -m 'Ready for deployment'")
                print("    git push origin main")
        except:
            print("  • 初始化Git仓库并推送到GitHub:")
            print("    git init")
            print("    git add .")
            print("    git commit -m 'Initial commit'")
            print("    git remote add origin https://github.com/yourusername/laopen.git")
            print("    git push -u origin main")
        
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
