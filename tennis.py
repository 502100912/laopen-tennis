#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LaOpen 网球管理模块 - 简化版
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
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
    """重定向到赛事管理页面"""
    return redirect(url_for('tennis.management'))

@tennis_bp.route('/management')
@login_required
def management():
    """赛事管理页面 - 有侧边栏可切换创建比赛和生成对阵表"""
    return render_template('matches/management.html')

@tennis_bp.route('/generate_matchup', methods=['GET', 'POST'])
@login_required
def generate_matchup():
    """生成随机对阵表页面"""
    if request.method == 'POST':
        # 处理对阵表生成逻辑
        from match_rule import MatchupGenerator
        import re
        
        match_format = request.form.get('match_format', '').strip()
        matchup_type = request.form.get('matchup_type', '').strip()
        rounds = int(request.form.get('rounds', 1))
        courts_count = int(request.form.get('courts_count', 1))
        participants_text = request.form.get('participants', '').strip()
        group_a_text = request.form.get('group_a', '').strip()
        group_b_text = request.form.get('group_b', '').strip()
        courts_text = request.form.get('courts', '').strip()
        
        # 验证基本参数
        if not match_format or not matchup_type:
            flash('Please select match format and matchup type', 'error')
            return render_template('matches/generate_matchup.html', 
                                 match_format=match_format,
                                 matchup_type=matchup_type,
                                 participants_text=participants_text,
                                 group_a_text=group_a_text,
                                 group_b_text=group_b_text,
                                 courts_text=courts_text,
                                 courts_count=courts_count,
                                 rounds=rounds)
        
        # 解析参与者名单 - 根据matchup_type处理不同输入
        participants = []
        group_a = []
        group_b = []
        
        if matchup_type == 'TeamRandom':
            # TeamRandom模式：解析GroupA和GroupB
            if not group_a_text or not group_b_text:
                flash('Please enter players for both Group A and Group B', 'error')
                return render_template('matches/generate_matchup.html',
                                     match_format=match_format,
                                     matchup_type=matchup_type,
                                     group_a_text=group_a_text,
                                     group_b_text=group_b_text,
                                     courts_text=courts_text,
                                     courts_count=courts_count,
                                     rounds=rounds)
            
            group_a = re.split(r'[,\s\n]+', group_a_text)
            group_a = [p.strip() for p in group_a if p.strip()]
            group_b = re.split(r'[,\s\n]+', group_b_text)
            group_b = [p.strip() for p in group_b if p.strip()]
            
            if len(group_a) < 2 or len(group_b) < 2:
                flash('Each group must have at least 2 players', 'error')
                return render_template('matches/generate_matchup.html',
                                     match_format=match_format,
                                     matchup_type=matchup_type,
                                     group_a_text=group_a_text,
                                     group_b_text=group_b_text,
                                     courts_text=courts_text,
                                     courts_count=courts_count,
                                     rounds=rounds)
            
            participants = group_a + group_b
            
        else:  # AllRandom模式
            if not participants_text:
                flash('Please enter player names', 'error')
                return render_template('matches/generate_matchup.html',
                                     match_format=match_format,
                                     matchup_type=matchup_type,
                                     participants_text=participants_text,
                                     courts_text=courts_text,
                                     courts_count=courts_count,
                                     rounds=rounds)
            
            participants = re.split(r'[,\s\n]+', participants_text)
            participants = [p.strip() for p in participants if p.strip()]
        
        # 验证人数和比赛格式的匹配
        if match_format == 'singles':
            if len(participants) < 4 or len(participants) % 2 != 0:
                flash('Singles requires even number of players (minimum 4)', 'error')
                return render_template('matches/generate_matchup.html',
                                     match_format=match_format,
                                     matchup_type=matchup_type,
                                     participants_text=participants_text,
                                     group_a_text=group_a_text,
                                     group_b_text=group_b_text,
                                     courts_text=courts_text,
                                     courts_count=courts_count,
                                     rounds=rounds)
        elif match_format == 'doubles':
            if len(participants) < 4 or len(participants) % 4 != 0:
                flash('Doubles requires players divisible by 4 (minimum 4)', 'error')
                return render_template('matches/generate_matchup.html',
                                     match_format=match_format,
                                     matchup_type=matchup_type,
                                     participants_text=participants_text,
                                     group_a_text=group_a_text,
                                     group_b_text=group_b_text,
                                     courts_text=courts_text,
                                     courts_count=courts_count,
                                     rounds=rounds)
        
        # 解析场地名单 - 支持换行/空格/逗号分割
        court_names = []
        if courts_text:
            court_names = re.split(r'[,\s\n]+', courts_text)
            court_names = [c.strip() for c in court_names if c.strip()]
        
        # 如果没有提供场地名，根据场地数量自动生成
        if not court_names:
            court_names = ['Court ' + str(i+1) for i in range(courts_count)]
        
        try:
            generator = MatchupGenerator()
            
            # 准备传递给generator的参数
            if matchup_type == 'TeamRandom':
                matchups = generator.generate_team_matchups(
                    match_format=match_format,
                    group_a=group_a,
                    group_b=group_b,
                    court_names=court_names,
                    rounds=rounds
                )
            else:  # AllRandom
                matchups = generator.generate_random_matchups(
                    match_format=match_format,
                    participants=participants,
                    court_names=court_names,
                    rounds=rounds
                )
            
            return render_template('matches/generate_matchup.html', 
                                 matchups=matchups,
                                 match_format=match_format,
                                 matchup_type=matchup_type,
                                 participants_text=participants_text,
                                 group_a_text=group_a_text,
                                 group_b_text=group_b_text,
                                 courts_text=courts_text,
                                 courts_count=courts_count,
                                 rounds=rounds)
        except Exception as e:
            flash('Failed to generate matchups: ' + str(e), 'error')
            return render_template('matches/generate_matchup.html',
                                 match_format=match_format,
                                 matchup_type=matchup_type,
                                 participants_text=participants_text,
                                 group_a_text=group_a_text,
                                 group_b_text=group_b_text,
                                 courts_text=courts_text,
                                 courts_count=courts_count,
                                 rounds=rounds)
    
    return render_template('matches/generate_matchup.html')