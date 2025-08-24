#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LaOpen 网球管理模块 - 简化版
"""

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from models import db, User, Match, Game

# 创建网球蓝图
tennis_bp = Blueprint('tennis', __name__, url_prefix='/tennis')

@tennis_bp.route('/dashboard')
@login_required
def dashboard():
    """网球Dashboard - 简洁主页"""
    
    # 获取用户的下一场比赛 (从Game表中查找)
    next_match = Game.query.filter(
        (Game.player1_id == current_user.id) | (Game.player3_id == current_user.id),
        Game.status == 'scheduled',
        Game.scheduled_time > datetime.utcnow()
    ).order_by(Game.scheduled_time.asc()).first()
    
    # 获取最近3场比赛记录 (从Game表中查找)
    recent_matches = Game.query.filter(
        (Game.player1_id == current_user.id) | (Game.player3_id == current_user.id),
        Game.status == 'finished'
    ).order_by(Game.updated_at.desc()).limit(3).all()
    
    return render_template('tennis/dashboard.html', 
                         next_match=next_match,
                         recent_matches=recent_matches)

# 简化的功能页面
@tennis_bp.route('/rankings')
@login_required
def rankings():
    """排行榜页面"""
    return "🏆 Rankings Coming Soon!<br><br><a href='/tennis/dashboard'>← Back</a>"

@tennis_bp.route('/matches')
@login_required
def matches():
    """重定向到赛事管理页面"""
    return redirect(url_for('match_mgmt.match_list'))

@tennis_bp.route('/join')
@login_required
def join_match():
    """加入比赛页面"""
    return "🎯 Join Coming Soon!<br><br><a href='/tennis/dashboard'>← Back</a>"

@tennis_bp.route('/create')
@login_required
def create_match():
    """重定向到创建赛事页面"""
    return redirect(url_for('match_mgmt.create_match'))