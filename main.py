#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LaOpen 主页面模块
处理首页和基础页面路由
"""

from flask import Blueprint, render_template, request
from flask_login import login_required, current_user

# 创建主页面蓝图
main_bp = Blueprint('main', __name__)

def is_mobile_device():
    """检测是否为移动设备"""
    user_agent = request.headers.get('User-Agent', '').lower()
    mobile_keywords = ['mobile', 'android', 'iphone', 'ipad', 'ipod', 'blackberry', 'iemobile']
    return any(keyword in user_agent for keyword in mobile_keywords)

@main_bp.route('/')
def index():
    """首页 - 自动适配移动端"""
    if is_mobile_device():
        return render_template('index_mobile.html')
    else:
        return render_template('index.html')

@main_bp.route('/mobile')
def mobile_index():
    """强制显示移动端版本"""
    return render_template('index_mobile.html')

# 用户中心路由已移除 - 直接使用 /tennis/dashboard
