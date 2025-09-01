#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LaOpen 数据库模型
包含用户模型和网球相关数据模型
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import bcrypt

# 数据库实例
db = SQLAlchemy()

class User(UserMixin, db.Model):
    """网球球员模型"""
    __tablename__ = 'users'
    
    # 基本信息
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(50), nullable=False, unique=True)
    phone = db.Column(db.String(11), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # 网球相关字段
    skill_level = db.Column(db.String(20), default='beginner')  # beginner/intermediate/advanced/pro
    rating = db.Column(db.Integer, default=1000)               # ELO积分
    total_wins = db.Column(db.Integer, default=0)              # 总胜场
    total_losses = db.Column(db.Integer, default=0)            # 总败场
    is_admin = db.Column(db.Boolean, default=False)            # 是否管理员
    last_played = db.Column(db.DateTime, nullable=True)        # 最后比赛时间
    
    def set_password(self, password):
        """设置密码哈希"""
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    def check_password(self, password):
        """验证密码"""
        password_bytes = password.encode('utf-8')
        hash_bytes = self.password_hash.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    
    @property
    def win_rate(self):
        """计算胜率"""
        if self.total_wins + self.total_losses == 0:
            return 0.0
        return round(self.total_wins / (self.total_wins + self.total_losses) * 100, 1)
    
    @property
    def current_rank(self):
        """获取当前排名"""
        higher_rated = User.query.filter(User.rating > self.rating).count()
        return higher_rated + 1
    
    def __repr__(self):
        return f'<User {self.nickname} ({self.rating}pts)>'

# 赛事参与者关联表
match_participants = db.Table('match_participants',
    db.Column('match_id', db.Integer, db.ForeignKey('matches.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('joined_at', db.DateTime, default=datetime.utcnow)
)

class Match(db.Model):
    """赛事模型 - 一个赛事包含多场比赛"""
    __tablename__ = 'matches'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # 赛事时间和地点
    start_datetime = db.Column(db.DateTime, nullable=False)        # 开始时间
    end_datetime = db.Column(db.DateTime, nullable=True)          # 结束时间
    location = db.Column(db.String(200), nullable=False)          # 地点
    
    # 赛事设置
    match_password = db.Column(db.String(50), nullable=False)      # 加入密码
    max_participants = db.Column(db.Integer, default=32)          # 最大参与人数
    match_type = db.Column(db.String(20), default='singles')      # singles/doubles/mixed
    tournament_type = db.Column(db.String(20), default='knockout') # knockout/round_robin
    
    # 比赛规则设置 (新增)
    court_count = db.Column(db.Integer, default=1)                # 场地数量
    round_count = db.Column(db.Integer, default=1)                # 比赛轮数
    court_list = db.Column(db.Text, nullable=True)                # 场地列表，JSON格式存储
    
    # 状态管理
    status = db.Column(db.String(20), default='preparing')        # preparing/registering/ongoing/finished/cancelled
    registration_deadline = db.Column(db.DateTime, nullable=True) # 报名截止时间
    
    # 创建信息
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_matches')
    participants = db.relationship('User', secondary=match_participants, 
                                 backref=db.backref('joined_matches', lazy='dynamic'))
    games = db.relationship('Game', backref='match', lazy=True, cascade='all, delete-orphan')
    
    @property
    def participant_count(self):
        """获取当前参与人数"""
        return len(self.participants)
    
    @property
    def is_full(self):
        """检查是否已满员"""
        return self.participant_count >= self.max_participants
    
    @property
    def can_register(self):
        """检查是否可以报名"""
        if self.status != 'registering':
            return False
        if self.is_full:
            return False
        if self.registration_deadline and datetime.utcnow() > self.registration_deadline:
            return False
        return True
    
    def get_courts(self):
        """获取场地列表"""
        if self.court_list:
            import json
            try:
                return json.loads(self.court_list)
            except:
                return []
        return []
    
    def set_courts(self, courts):
        """设置场地列表"""
        import json
        if isinstance(courts, list):
            self.court_list = json.dumps(courts)
            self.court_count = len(courts)
        else:
            self.court_list = None
            self.court_count = 1
    
    def is_participant(self, user):
        """检查用户是否已参与"""
        return user in self.participants
    
    def __repr__(self):
        return f'<Match {self.name} ({self.participant_count}/{self.max_participants})>'

class Game(db.Model):
    """比赛模型 - 一场具体的比赛"""
    __tablename__ = 'games'
    
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=False)
    
    # 比赛信息
    game_type = db.Column(db.String(20), default='singles')       # singles/doubles
    round_name = db.Column(db.String(50), nullable=True)          # 轮次名称 (如 "Quarter Final")
    round_number = db.Column(db.Integer, default=1)               # 轮次序号
    
    # 参赛选手 (最多4人，单打用前2个，双打用全部4个)
    player1_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    player2_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # 双打时player1的队友
    player3_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    player4_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # 双打时player3的队友
    
    # 比赛时间和场地
    scheduled_time = db.Column(db.DateTime, nullable=True)        # 预定时间
    actual_start_time = db.Column(db.DateTime, nullable=True)     # 实际开始时间
    actual_end_time = db.Column(db.DateTime, nullable=True)       # 实际结束时间
    court = db.Column(db.String(50), nullable=True)              # 场地
    
    # 比赛状态和结果
    status = db.Column(db.String(20), default='scheduled')       # scheduled/playing/finished/cancelled
    winner_team = db.Column(db.Integer, default=0)               # 获胜队伍 (1或3，分别代表player1/2队或player3/4队)
    
    # 比分信息 (支持多盘制)
    set1_team1_score = db.Column(db.Integer, default=0)
    set1_team2_score = db.Column(db.Integer, default=0)
    set2_team1_score = db.Column(db.Integer, default=0)
    set2_team2_score = db.Column(db.Integer, default=0)
    set3_team1_score = db.Column(db.Integer, default=0)
    set3_team2_score = db.Column(db.Integer, default=0)
    
    # 额外信息
    notes = db.Column(db.Text, nullable=True)                    # 比赛备注
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    player1 = db.relationship('User', foreign_keys=[player1_id])
    player2 = db.relationship('User', foreign_keys=[player2_id])
    player3 = db.relationship('User', foreign_keys=[player3_id])
    player4 = db.relationship('User', foreign_keys=[player4_id])
    
    @property
    def is_finished(self):
        """比赛是否结束"""
        return self.status == 'finished'
    
    @property
    def is_doubles(self):
        """是否为双打"""
        return self.game_type == 'doubles'
    
    @property
    def team1_players(self):
        """获取队伍1的选手"""
        if self.is_doubles:
            return [p for p in [self.player1, self.player2] if p]
        else:
            return [self.player1] if self.player1 else []
    
    @property
    def team2_players(self):
        """获取队伍2的选手"""
        if self.is_doubles:
            return [p for p in [self.player3, self.player4] if p]
        else:
            return [self.player3] if self.player3 else []
    
    @property
    def score_summary(self):
        """获取比分摘要"""
        sets = []
        if self.set1_team1_score > 0 or self.set1_team2_score > 0:
            sets.append(f"{self.set1_team1_score}-{self.set1_team2_score}")
        if self.set2_team1_score > 0 or self.set2_team2_score > 0:
            sets.append(f"{self.set2_team1_score}-{self.set2_team2_score}")
        if self.set3_team1_score > 0 or self.set3_team2_score > 0:
            sets.append(f"{self.set3_team1_score}-{self.set3_team2_score}")
        return " | ".join(sets) if sets else "0-0"
    
    def get_opponent_team(self, user_id):
        """获取指定用户的对手队伍"""
        team1_ids = [p.id for p in self.team1_players]
        team2_ids = [p.id for p in self.team2_players]
        
        if user_id in team1_ids:
            return self.team2_players
        elif user_id in team2_ids:
            return self.team1_players
        return []
    
    def get_result_for_user(self, user_id):
        """获取指定用户的比赛结果"""
        if not self.is_finished or self.winner_team == 0:
            return 'pending'
        
        team1_ids = [p.id for p in self.team1_players]
        team2_ids = [p.id for p in self.team2_players]
        
        if user_id in team1_ids and self.winner_team == 1:
            return 'win'
        elif user_id in team2_ids and self.winner_team == 2:
            return 'win'
        elif user_id in team1_ids or user_id in team2_ids:
            return 'loss'
        return 'unknown'
    
    def __repr__(self):
        team1_names = " & ".join([p.nickname for p in self.team1_players])
        team2_names = " & ".join([p.nickname for p in self.team2_players])
        return f'<Game {team1_names} vs {team2_names}>'

def init_db(app):
    """初始化数据库表"""
    with app.app_context():
        try:
            db.create_all()
            print("✅ 数据库表创建成功！")
            return True
        except Exception as e:
            print(f"❌ 数据库初始化失败：{e}")
            print("请检查数据库配置")
            return False
