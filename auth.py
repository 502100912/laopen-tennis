#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LaOpen 认证模块
处理用户注册、登录、登出等认证相关功能
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User
from forms import RegistrationForm, LoginForm

# 创建认证蓝图
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    form = RegistrationForm()
    
    if form.validate_on_submit():
        # 检查昵称是否已存在
        if User.query.filter_by(nickname=form.nickname.data).first():
            flash('NickName already exists, please choose another one', 'error')
            return render_template('register.html', form=form)
        
        # 检查手机号是否已注册
        if User.query.filter_by(phone=form.phone.data).first():
            flash('Phone number already registered, please login directly', 'error')
            return render_template('register.html', form=form)
        
        try:
            # 创建新用户
            user = User(
                nickname=form.nickname.data,
                phone=form.phone.data
            )
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please login', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('Registration failed, please try again', 'error')
            print(f"注册错误：{e}")
    
    return render_template('register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(phone=form.phone.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash(f'Welcome back, {user.nickname}!', 'success')
            
            # 检查是否有next参数（用户尝试访问需要登录的页面）
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('tennis.dashboard'))
        else:
            flash('Phone number or password is incorrect', 'error')
    
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """用户登出"""
    username = current_user.nickname
    logout_user()
    flash(f'Goodbye, {username}! Successfully logged out', 'info')
    return redirect(url_for('main.index'))

def init_auth(login_manager):
    """初始化登录管理器"""
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please login to access this page'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
