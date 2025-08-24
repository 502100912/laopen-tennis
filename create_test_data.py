#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建测试数据脚本
为网球系统创建示例用户、赛事和比赛数据
"""

from datetime import datetime, timedelta
import random
from app import create_app
from models import db, User, Match, Game

def create_test_data():
    """创建测试数据"""
    app = create_app()
    
    with app.app_context():
        print("🎾 开始创建测试数据...")
        print("=" * 50)
        
        # 1. 创建 20 个测试用户
        print("👥 创建测试用户...")
        users_data = [
            {'nickname': 'Alice', 'phone': '13800000001', 'rating': 1650, 'skill_level': 'advanced', 'total_wins': 25, 'total_losses': 8},
            {'nickname': 'Bob', 'phone': '13800000002', 'rating': 1580, 'skill_level': 'advanced', 'total_wins': 22, 'total_losses': 10},
            {'nickname': 'Charlie', 'phone': '13800000003', 'rating': 1520, 'skill_level': 'intermediate', 'total_wins': 18, 'total_losses': 12},
            {'nickname': 'Diana', 'phone': '13800000004', 'rating': 1480, 'skill_level': 'intermediate', 'total_wins': 15, 'total_losses': 15},
            {'nickname': 'Eve', 'phone': '13800000005', 'rating': 1420, 'skill_level': 'intermediate', 'total_wins': 12, 'total_losses': 18},
            {'nickname': 'Frank', 'phone': '13800000006', 'rating': 1380, 'skill_level': 'beginner', 'total_wins': 8, 'total_losses': 22},
            {'nickname': 'Grace', 'phone': '13800000007', 'rating': 1350, 'skill_level': 'beginner', 'total_wins': 6, 'total_losses': 24},
            {'nickname': 'Henry', 'phone': '13800000008', 'rating': 1600, 'skill_level': 'advanced', 'total_wins': 28, 'total_losses': 7},
            {'nickname': 'Ivy', 'phone': '13800000009', 'rating': 1450, 'skill_level': 'intermediate', 'total_wins': 14, 'total_losses': 16},
            {'nickname': 'Jack', 'phone': '13800000010', 'rating': 1320, 'skill_level': 'beginner', 'total_wins': 5, 'total_losses': 25},
            {'nickname': 'Kate', 'phone': '13800000011', 'rating': 1550, 'skill_level': 'intermediate', 'total_wins': 20, 'total_losses': 12},
            {'nickname': 'Leo', 'phone': '13800000012', 'rating': 1400, 'skill_level': 'intermediate', 'total_wins': 11, 'total_losses': 19},
            {'nickname': 'Mia', 'phone': '13800000013', 'rating': 1280, 'skill_level': 'beginner', 'total_wins': 4, 'total_losses': 26},
            {'nickname': 'Noah', 'phone': '13800000014', 'rating': 1620, 'skill_level': 'advanced', 'total_wins': 30, 'total_losses': 5},
            {'nickname': 'Olivia', 'phone': '13800000015', 'rating': 1500, 'skill_level': 'intermediate', 'total_wins': 16, 'total_losses': 14},
            {'nickname': 'Paul', 'phone': '13800000016', 'rating': 1360, 'skill_level': 'beginner', 'total_wins': 7, 'total_losses': 23},
            {'nickname': 'Quinn', 'phone': '13800000017', 'rating': 1440, 'skill_level': 'intermediate', 'total_wins': 13, 'total_losses': 17},
            {'nickname': 'Ruby', 'phone': '13800000018', 'rating': 1590, 'skill_level': 'advanced', 'total_wins': 24, 'total_losses': 9},
            {'nickname': 'Sam', 'phone': '13800000019', 'rating': 1300, 'skill_level': 'beginner', 'total_wins': 3, 'total_losses': 27},
            {'nickname': 'Tina', 'phone': '13800000020', 'rating': 1470, 'skill_level': 'intermediate', 'total_wins': 15, 'total_losses': 15},
        ]
        
        created_users = []
        for user_data in users_data:
            # 检查用户是否已存在
            existing_user = User.query.filter_by(nickname=user_data['nickname']).first()
            if existing_user:
                print(f"  ⚠️  用户 {user_data['nickname']} 已存在，跳过创建")
                created_users.append(existing_user)
                continue
                
            user = User(
                nickname=user_data['nickname'],
                phone=user_data['phone'],
                rating=user_data['rating'],
                skill_level=user_data['skill_level'],
                total_wins=user_data['total_wins'],
                total_losses=user_data['total_losses'],
                is_admin=(user_data['nickname'] == 'Alice'),  # Alice 设为管理员
                last_played=datetime.utcnow() - timedelta(days=random.randint(1, 30))
            )
            user.set_password('password123')  # 统一密码便于测试
            created_users.append(user)
            db.session.add(user)
            print(f"  ✅ 创建用户: {user_data['nickname']} (Rating: {user_data['rating']})")
        
        db.session.commit()
        print(f"📊 总用户数: {len(created_users)}")
        
        # 2. 创建一场测试赛事
        print("\n🏆 创建测试赛事...")
        
        # 检查是否已存在测试赛事
        existing_match = Match.query.filter_by(name='Spring Tennis Championship 2024').first()
        if existing_match:
            print("  ⚠️  测试赛事已存在，删除并重新创建...")
            # 删除关联的 games
            Game.query.filter_by(match_id=existing_match.id).delete()
            # 删除赛事
            db.session.delete(existing_match)
            db.session.commit()
        
        test_match = Match(
            name='Spring Tennis Championship 2024',
            description='Annual spring tennis tournament featuring both singles and doubles matches. Open to all skill levels!',
            start_datetime=datetime.utcnow() + timedelta(days=7),  # 一周后开始
            end_datetime=datetime.utcnow() + timedelta(days=9),    # 持续3天
            location='Central Tennis Club, Courts 1-6',
            match_password='tennis2024',
            max_participants=16,
            match_type='mixed',  # 混合比赛（单打+双打）
            tournament_type='knockout',  # 淘汰赛
            status='registering',  # 正在报名
            registration_deadline=datetime.utcnow() + timedelta(days=5),  # 5天后报名截止
            created_by=created_users[0].id  # Alice 创建
        )
        db.session.add(test_match)
        db.session.commit()
        print(f"  ✅ 创建赛事: {test_match.name}")
        print(f"     📍 地点: {test_match.location}")
        print(f"     📅 时间: {test_match.start_datetime.strftime('%Y-%m-%d %H:%M')}")
        print(f"     🔑 密码: {test_match.match_password}")
        print(f"     👥 最大参与人数: {test_match.max_participants}")
        
        # 3. 让部分用户加入赛事
        print("\n👥 用户加入赛事...")
        participants = random.sample(created_users, 8)  # 随机选择8个用户参与
        for user in participants:
            test_match.participants.append(user)
            print(f"  ✅ {user.nickname} 加入赛事")
        
        db.session.commit()
        print(f"📊 参与人数: {len(participants)}/{test_match.max_participants}")
        
        # 4. 创建一些测试比赛
        print("\n🎯 创建测试比赛...")
        
        # 创建第一轮单打比赛
        games_created = []
        
        # 4场单打比赛（8人，两两对战）
        singles_players = participants[:8]  # 使用前8个参与者
        for i in range(0, len(singles_players), 2):
            if i + 1 < len(singles_players):
                player1 = singles_players[i]
                player2 = singles_players[i + 1]
                
                game = Game(
                    match_id=test_match.id,
                    game_type='singles',
                    round_name='First Round',
                    round_number=1,
                    player1_id=player1.id,
                    player2_id=None,  # 单打不需要队友
                    player3_id=player2.id,
                    player4_id=None,  # 单打不需要队友
                    scheduled_time=datetime.utcnow() + timedelta(days=7, hours=random.randint(9, 17)),
                    court=f"Court {random.choice(['A', 'B', 'C', 'D'])}",
                    status='scheduled'
                )
                
                # 模拟一些已完成的比赛结果
                if random.random() < 0.3:  # 30% 概率设置为已完成
                    game.status = 'finished'
                    game.actual_start_time = game.scheduled_time
                    game.actual_end_time = game.scheduled_time + timedelta(hours=2)
                    
                    # 模拟比分 (基于rating差异)
                    rating_diff = player1.rating - player2.rating
                    win_probability = 0.5 + (rating_diff / 1000) * 0.3
                    
                    if random.random() < win_probability:
                        game.winner_team = 1  # player1 获胜
                        game.set1_team1_score, game.set1_team2_score = 6, random.randint(0, 4)
                        game.set2_team1_score, game.set2_team2_score = 6, random.randint(2, 4)
                    else:
                        game.winner_team = 2  # player2 获胜
                        game.set1_team1_score, game.set1_team2_score = random.randint(0, 4), 6
                        game.set2_team1_score, game.set2_team2_score = random.randint(2, 4), 6
                
                games_created.append(game)
                db.session.add(game)
                print(f"  ✅ 单打比赛: {player1.nickname} vs {player2.nickname} ({game.status})")
        
        # 创建2场双打比赛（需要4人一组）
        if len(participants) >= 8:
            doubles_players = participants[:8]
            
            # 第一场双打
            game = Game(
                match_id=test_match.id,
                game_type='doubles',
                round_name='First Round',
                round_number=1,
                player1_id=doubles_players[0].id,  # 队伍1
                player2_id=doubles_players[1].id,
                player3_id=doubles_players[2].id,  # 队伍2
                player4_id=doubles_players[3].id,
                scheduled_time=datetime.utcnow() + timedelta(days=8, hours=random.randint(9, 17)),
                court=f"Court {random.choice(['E', 'F'])}",
                status='scheduled'
            )
            games_created.append(game)
            db.session.add(game)
            print(f"  ✅ 双打比赛: {doubles_players[0].nickname} & {doubles_players[1].nickname} vs {doubles_players[2].nickname} & {doubles_players[3].nickname}")
            
            # 第二场双打
            game = Game(
                match_id=test_match.id,
                game_type='doubles',
                round_name='First Round',
                round_number=1,
                player1_id=doubles_players[4].id,  # 队伍1
                player2_id=doubles_players[5].id,
                player3_id=doubles_players[6].id,  # 队伍2
                player4_id=doubles_players[7].id,
                scheduled_time=datetime.utcnow() + timedelta(days=8, hours=random.randint(9, 17)),
                court=f"Court {random.choice(['E', 'F'])}",
                status='scheduled'
            )
            games_created.append(game)
            db.session.add(game)
            print(f"  ✅ 双打比赛: {doubles_players[4].nickname} & {doubles_players[5].nickname} vs {doubles_players[6].nickname} & {doubles_players[7].nickname}")
        
        db.session.commit()
        print(f"📊 创建比赛数: {len(games_created)}")
        
        # 5. 显示创建摘要
        print("\n" + "=" * 50)
        print("🎉 测试数据创建完成!")
        print("=" * 50)
        print(f"👥 用户总数: {User.query.count()}")
        print(f"🏆 赛事总数: {Match.query.count()}")
        print(f"🎯 比赛总数: {Game.query.count()}")
        
        print(f"\n🔐 登录信息:")
        print(f"  管理员账号: Alice")
        print(f"  手机号: 13800000001")
        print(f"  密码: password123")
        
        print(f"\n🏆 测试赛事信息:")
        print(f"  赛事名称: {test_match.name}")
        print(f"  加入密码: {test_match.match_password}")
        print(f"  参与人数: {len(test_match.participants)}/{test_match.max_participants}")
        print(f"  状态: {test_match.status}")
        
        print(f"\n🚀 现在可以启动应用并使用以下用户测试:")
        for user in participants[:5]:  # 显示前5个参与者
            print(f"  • {user.nickname} (Rating: {user.rating}) - {user.phone}")
        
        print(f"\n💡 测试建议:")
        print(f"  1. 使用不同用户登录查看仪表板")
        print(f"  2. 访问 /matches 查看赛事列表")
        print(f"  3. 使用密码 '{test_match.match_password}' 加入赛事")
        print(f"  4. 查看赛事详情和比赛安排")

if __name__ == '__main__':
    create_test_data()