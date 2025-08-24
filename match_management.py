#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LaOpen 赛事管理模块
处理赛事列表、赛事详情、用户加入赛事等功能
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from models import db, Match, Game, User

# 创建赛事管理蓝图
match_mgmt_bp = Blueprint('match_mgmt', __name__, url_prefix='/matches')

@match_mgmt_bp.route('/')
@login_required
def match_list():
    """赛事列表页面"""
    
    # 获取所有可见的赛事
    matches = Match.query.filter(
        Match.status.in_(['preparing', 'registering', 'ongoing'])
    ).order_by(Match.start_datetime.asc()).all()
    
    # 分类赛事
    upcoming_matches = []  # 即将开始的赛事
    ongoing_matches = []   # 正在进行的赛事
    registering_matches = []  # 正在报名的赛事
    
    for match in matches:
        if match.status == 'registering':
            registering_matches.append(match)
        elif match.status == 'ongoing':
            ongoing_matches.append(match)
        elif match.status == 'preparing':
            upcoming_matches.append(match)
    
    # 获取用户已参与的赛事
    user_matches = current_user.joined_matches.filter(
        Match.status.in_(['preparing', 'registering', 'ongoing'])
    ).all()
    
    return render_template('matches/match_list.html',
                         upcoming_matches=upcoming_matches,
                         ongoing_matches=ongoing_matches,
                         registering_matches=registering_matches,
                         user_matches=user_matches)

@match_mgmt_bp.route('/<int:match_id>')
@login_required
def match_detail(match_id):
    """赛事详情页面"""
    
    match = Match.query.get_or_404(match_id)
    
    # 检查用户是否已参与
    is_participant = match.is_participant(current_user)
    
    # 获取赛事中的所有比赛
    games = Game.query.filter_by(match_id=match_id).order_by(
        Game.round_number.asc(),
        Game.scheduled_time.asc()
    ).all()
    
    # 按轮次分组比赛
    games_by_round = {}
    for game in games:
        round_key = f"Round {game.round_number}"
        if game.round_name:
            round_key = game.round_name
        
        if round_key not in games_by_round:
            games_by_round[round_key] = []
        games_by_round[round_key].append(game)
    
    return render_template('matches/match_detail.html',
                         match=match,
                         is_participant=is_participant,
                         games_by_round=games_by_round,
                         participants=match.participants)

@match_mgmt_bp.route('/<int:match_id>/join', methods=['POST'])
@login_required
def join_match(match_id):
    """用户加入赛事"""
    
    match = Match.query.get_or_404(match_id)
    password = request.form.get('password', '').strip()
    
    # 验证加入条件
    if match.is_participant(current_user):
        flash('You have already joined this match!', 'info')
        return redirect(url_for('match_mgmt.match_detail', match_id=match_id))
    
    if not match.can_register:
        flash('Registration is not available for this match.', 'error')
        return redirect(url_for('match_mgmt.match_detail', match_id=match_id))
    
    if password != match.match_password:
        flash('Incorrect password!', 'error')
        return redirect(url_for('match_mgmt.match_detail', match_id=match_id))
    
    # 加入赛事
    try:
        match.participants.append(current_user)
        db.session.commit()
        flash(f'Successfully joined {match.name}!', 'success')
        
        # 如果赛事满员，自动更改状态
        if match.is_full and match.status == 'registering':
            match.status = 'preparing'
            db.session.commit()
            flash('Match is now full and ready to start!', 'info')
            
    except Exception as e:
        db.session.rollback()
        flash('Failed to join match. Please try again.', 'error')
    
    return redirect(url_for('match_mgmt.match_detail', match_id=match_id))

@match_mgmt_bp.route('/<int:match_id>/leave', methods=['POST'])
@login_required
def leave_match(match_id):
    """用户离开赛事"""
    
    match = Match.query.get_or_404(match_id)
    
    if not match.is_participant(current_user):
        flash('You are not a participant in this match.', 'error')
        return redirect(url_for('match_mgmt.match_detail', match_id=match_id))
    
    if match.status not in ['preparing', 'registering']:
        flash('Cannot leave a match that has already started.', 'error')
        return redirect(url_for('match_mgmt.match_detail', match_id=match_id))
    
    try:
        match.participants.remove(current_user)
        db.session.commit()
        flash(f'Successfully left {match.name}.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Failed to leave match. Please try again.', 'error')
    
    return redirect(url_for('match_mgmt.match_list'))

@match_mgmt_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_match():
    """创建新赛事"""
    
    if request.method == 'POST':
        # 获取表单数据
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        location = request.form.get('location', '').strip()
        start_datetime = request.form.get('start_datetime')
        match_password = request.form.get('password', '').strip()
        max_participants = int(request.form.get('max_participants', 32))
        match_type = request.form.get('match_type', 'singles')
        tournament_type = request.form.get('tournament_type', 'knockout')
        
        # 基本验证
        if not all([name, location, start_datetime, match_password]):
            flash('Please fill in all required fields.', 'error')
            return render_template('matches/create_match.html')
        
        try:
            # 解析时间
            start_dt = datetime.strptime(start_datetime, '%Y-%m-%dT%H:%M')
            
            # 创建新赛事
            new_match = Match(
                name=name,
                description=description,
                location=location,
                start_datetime=start_dt,
                match_password=match_password,
                max_participants=max_participants,
                match_type=match_type,
                tournament_type=tournament_type,
                status='registering',
                created_by=current_user.id
            )
            
            db.session.add(new_match)
            db.session.commit()
            
            flash(f'Match "{name}" created successfully!', 'success')
            return redirect(url_for('match_mgmt.match_detail', match_id=new_match.id))
            
        except ValueError:
            flash('Invalid date format. Please use the date picker.', 'error')
        except Exception as e:
            db.session.rollback()
            flash('Failed to create match. Please try again.', 'error')
    
    return render_template('matches/create_match.html')

# 用于JSON API的路由
@match_mgmt_bp.route('/api/matches')
@login_required
def api_matches():
    """获取赛事列表的API接口"""
    
    matches = Match.query.filter(
        Match.status.in_(['preparing', 'registering', 'ongoing'])
    ).order_by(Match.start_datetime.asc()).all()
    
    result = []
    for match in matches:
        result.append({
            'id': match.id,
            'name': match.name,
            'location': match.location,
            'start_datetime': match.start_datetime.isoformat(),
            'status': match.status,
            'participants': match.participant_count,
            'max_participants': match.max_participants,
            'match_type': match.match_type,
            'is_participant': match.is_participant(current_user),
            'can_register': match.can_register
        })
    
    return jsonify(result)

@match_mgmt_bp.route('/api/matches/<int:match_id>')
@login_required
def api_match_detail(match_id):
    """获取赛事详情的API接口"""
    
    match = Match.query.get_or_404(match_id)
    
    return jsonify({
        'id': match.id,
        'name': match.name,
        'description': match.description,
        'location': match.location,
        'start_datetime': match.start_datetime.isoformat(),
        'status': match.status,
        'participants': match.participant_count,
        'max_participants': match.max_participants,
        'match_type': match.match_type,
        'tournament_type': match.tournament_type,
        'is_participant': match.is_participant(current_user),
        'can_register': match.can_register,
        'games_count': len(match.games)
    })
