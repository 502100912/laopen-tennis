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
from match_rule import auto_generate_games, MatchRuleManager, MatchRuleError
from sqlalchemy import text

def create_user_data():
    """创建测试用户数据"""
    app = create_app()
    
    with app.app_context():
        print("🎾 创建测试用户数据...")
        print("=" * 60)
        
        # 预定义的用户组
        group_a_names = ["曲少", "生鱼片", "脱其", "winning", "阿将", "叉子", "Ethan", "默默", "丹丹", "LTT"]
        group_b_names = ["LU", "JuJu", "cherry", "zzz", "新一", "Leo", "大竣", "MiamiBoy", "尤老师", "luke"]
        all_names = group_a_names + group_b_names
        
        print(f"👥 A组队员 ({len(group_a_names)}人): {', '.join(group_a_names)}")
        print(f"👥 B组队员 ({len(group_b_names)}人): {', '.join(group_b_names)}")
        
        # 删除所有现有用户
        print(f"\n🗑️ 清理现有用户数据...")
        user_count = User.query.count()
        if user_count > 0:
            # 删除关联数据
            Game.query.delete()
            db.session.execute(text('DELETE FROM match_participants'))
            Match.query.delete()
            User.query.delete()
            db.session.commit()
            print(f"  ✅ 已删除 {user_count} 个现有用户及相关数据")
        else:
            print("  ℹ️ 没有现有用户数据需要清理")
        
        # 创建新用户
        print(f"\n🔧 创建新用户...")
        created_users = []
        
        for i, name in enumerate(all_names, 1):
            user = User(
                nickname=name,
                phone=f"1393000{i:04d}",  # 使用1393开头避免冲突
                rating=1200 + (i * 20) % 400,  # 随机积分1200-1600
                created_at=datetime.now(),
                is_admin=(name == "曲少"),  # 曲少设为管理员
                skill_level='intermediate' if 1300 <= (1200 + (i * 20) % 400) <= 1500 else ('advanced' if (1200 + (i * 20) % 400) > 1500 else 'beginner'),
                total_wins=random.randint(5, 30),
                total_losses=random.randint(5, 25),
                last_played=datetime.utcnow() - timedelta(days=random.randint(1, 30))
            )
            user.set_password('password123')  # 统一密码便于测试
            created_users.append(user)
            db.session.add(user)
            print(f"  ✅ 创建用户: {name} (积分: {user.rating}, 手机: {user.phone})")
        
        db.session.commit()
        print(f"\n📊 用户创建完成!")
        print(f"   总用户数: {len(created_users)}")
        print(f"   A组: {len(group_a_names)} 人")
        print(f"   B组: {len(group_b_names)} 人")
        print(f"   管理员: {created_users[0].nickname}")
        
        return created_users


def test_team_double_random():
    """创建测试赛事：20人，五片场地"""
    app = create_app()
    
    with app.app_context():
        print("\n🏆 创建测试团队双打赛事...")
        print("=" * 60)
        
        # 检查用户是否存在
        users = User.query.all()
        if len(users) < 20:
            print(f"❌ 用户数量不足：当前 {len(users)} 人，需要 20 人")
            print("   请先运行 create_user_data() 创建用户")
            return None
            
        # 删除现有的测试赛事
        existing_match = Match.query.filter_by(name='08.25 随机匹配团队双打').first()
        if existing_match:
            print("🗑️ 删除现有测试赛事...")
            Game.query.filter_by(match_id=existing_match.id).delete()
            db.session.delete(existing_match)
            db.session.commit()
        
        # 创建新赛事
        match_name = "08.25 随机匹配团队双打"
        courts = [2, 4, 5, 7, 8]  # 指定的场地列表
        
        match = Match(
            name=match_name,
            description="20人随机匹配团队双打，A组vs B组，5场地同时进行",
            start_datetime=datetime.now() + timedelta(days=1),  # 明天开始
            end_datetime=datetime.now() + timedelta(days=1, hours=6),  # 持续6小时
            location="网球中心 2,4,5,7,8号场地",
            match_password="team2024",
            max_participants=20,
            match_type="doubles",
            tournament_type="round_robin",
            court_count=5,  # 5个场地
            round_count=3,  # 3轮比赛
            created_by=users[0].id,  # 第一个用户作为创建者
            status="registering"
        )
        
        db.session.add(match)
        db.session.flush()  # 获取match.id
        
        # 设置场地信息
        match.set_courts(courts)
        print(f"🏟️ 设置场地信息: {courts}")
        
        # 添加所有20个用户为参与者
        print(f"\n👥 添加参与者到比赛...")
        for user in users[:20]:
            match.participants.append(user)
            print(f"  ✅ {user.nickname} 加入比赛")
        
        db.session.commit()
        
        print(f"\n📋 比赛创建完成:")
        print(f"  名称: {match.name}")
        print(f"  参与者: {len(match.participants)} 人")
        print(f"  场地数: {match.court_count} 个")
        print(f"  轮数: {match.round_count} 轮")
        print(f"  预期比赛场次: {match.court_count * match.round_count} 场")
        print(f"  开始时间: {match.start_datetime.strftime('%Y-%m-%d %H:%M')}")
        print(f"  地点: {match.location}")
        print(f"  密码: {match.match_password}")
        
        return match


def generate_game():
    """为测试赛事生成对阵表并输出"""
    app = create_app()
    
    with app.app_context():
        print("\n🚀 开始生成智能对局表...")
        print("=" * 60)
        
        # 查找测试赛事
        match = Match.query.filter_by(name='08.25 随机匹配团队双打').first()
        if not match:
            print("❌ 未找到测试赛事")
            print("   请先运行 test_team_double_random() 创建赛事")
            return
        
        # 准备预定义分组
        group_a_names = ["曲少", "生鱼片", "脱其", "winning", "阿将", "叉子", "Ethan", "默默", "丹丹", "LTT"]
        group_b_names = ["LU", "JuJu", "cherry", "zzz", "新一", "Leo", "大竣", "MiamiBoy", "尤老师", "luke"]
        
        group_a_users = []
        group_b_users = []
        
        # 根据名称找到对应的用户对象
        for name in group_a_names:
            user = User.query.filter_by(nickname=name).first()
            if user:
                group_a_users.append(user)
            else:
                print(f"❌ 找不到A组用户: {name}")
                return
        
        for name in group_b_names:
            user = User.query.filter_by(nickname=name).first()
            if user:
                group_b_users.append(user)
            else:
                print(f"❌ 找不到B组用户: {name}")
                return
        
        print(f"✅ A组已准备: {[u.nickname for u in group_a_users]}")
        print(f"✅ B组已准备: {[u.nickname for u in group_b_users]}")
        
        try:
            # 检查是否可以生成
            can_generate, reason = MatchRuleManager.can_generate_games(match)
            if not can_generate:
                print(f"❌ 无法生成对局表: {reason}")
                return
            
            # 生成对局
            games = auto_generate_games(match.id, 'total_random_double', (group_a_users, group_b_users))
            
            print(f"\n✅ 对局表生成完成！")
            print(f"📊 总结:")
            print(f"  • 成功创建 {len(games)} 场比赛")
            print(f"  • 每轮 {match.court_count} 场同时进行")
            print(f"  • 总共进行 {match.round_count} 轮")
            print(f"  • 每场比赛4人参与（双打）")
            
            # 显示详细对局安排
            print(f"\n📅 详细对局安排:")
            
            for round_num in range(1, match.round_count + 1):
                round_games = [g for g in games if g.round_number == round_num]
                
                # 按照预设的场地顺序排序
                court_order = ["场地 2", "场地 4", "场地 5", "场地 7", "场地 8"]
                round_games.sort(key=lambda g: court_order.index(g.court) if g.court in court_order else 999)
                
                print(f"\n🔸 第{round_num}轮 ({len(round_games)}场比赛):")
                
                for game in round_games:
                    team1 = f"{game.player1.nickname} + {game.player2.nickname}"
                    team2 = f"{game.player3.nickname} + {game.player4.nickname}"
                    time_str = game.scheduled_time.strftime('%H:%M')
                    print(f"  🏟️ {game.court} {time_str}:")
                    print(f"      {team1}")
                    print(f"                    VS")
                    print(f"      {team2}")
                    print()
                    
        except MatchRuleError as e:
            print(f"❌ 生成对局表失败: {str(e)}")
        except Exception as e:
            print(f"❌ 生成对局表时发生错误: {str(e)}")


def create_test_data():
    """完整的测试数据创建流程"""
    print("🎾 LaOpen 测试数据创建系统")
    print("=" * 60)
    
    # 1. 创建用户数据
    users = create_user_data()
    
    # 2. 创建测试赛事
    match = test_team_double_random()
    
    # 3. 生成对局表
    if match:
        generate_game()
    
    # 使用app context进行最终统计
    app = create_app()
    with app.app_context():
        print("\n" + "=" * 60)
        print("🎉 所有测试数据创建完成!")
        print("=" * 60)
        print(f"👥 用户总数: {User.query.count()}")
        print(f"🏆 赛事总数: {Match.query.count()}")  
        print(f"🎯 比赛总数: {Game.query.count()}")
        
        print(f"\n🔐 登录信息:")
        print(f"  管理员账号: 曲少")
        print(f"  手机号: 13930000001")
        print(f"  密码: password123")
        
        if match:
            print(f"\n🏆 测试赛事信息:")
            print(f"  赛事名称: {match.name}")
            print(f"  加入密码: {match.match_password}")
            print(f"  参与人数: {len(match.participants)}/{match.max_participants}")
            print(f"  状态: {match.status}")
        
        print(f"\n💡 测试建议:")
        print(f"  1. python3 create_test_data.py - 完整流程")
        print(f"  2. 单独运行各个函数进行测试")
        print(f"  3. 查看网页端的比赛效果")

if __name__ == '__main__':
    create_test_data()