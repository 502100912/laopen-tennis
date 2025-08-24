#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试比赛规则系统
演示如何使用 match_rule.py 生成自动对局表
"""

from app import create_app
from models import db, Match, Game, User
from match_rule import TotalRandomDouble, MatchRuleManager, auto_generate_games, MatchRuleError

def test_match_rule():
    """测试比赛规则系统"""
    app = create_app()
    
    with app.app_context():
        print("🎾 测试比赛规则系统")
        print("=" * 60)
        
        # 1. 获取现有赛事
        match = Match.query.filter_by(name='Spring Tennis Championship 2024').first()
        if not match:
            print("❌ 找不到测试赛事")
            return
        
        print(f"📋 赛事信息:")
        print(f"   名称: {match.name}")
        print(f"   场地数: {match.court_count}")
        print(f"   轮数: {match.round_count}")
        print(f"   参与者: {len(match.participants)} 人")
        print(f"   状态: {match.status}")
        
        # 2. 检查参与者
        print(f"\n👥 参与者列表:")
        for i, user in enumerate(match.participants, 1):
            print(f"   {i:2d}. {user.nickname:<10} (Rating: {user.rating})")
        
        # 3. 检查是否可以生成对局表
        can_generate, reason = MatchRuleManager.can_generate_games(match)
        print(f"\n🔍 检查结果: {'✅ 可以' if can_generate else '❌ 不可以'}")
        print(f"   原因: {reason}")
        
        if not can_generate:
            # 如果是已有比赛，清理一下再测试
            if "已有" in reason:
                print("\n🧹 清理现有比赛数据...")
                Game.query.filter_by(match_id=match.id).delete()
                db.session.commit()
                print("✅ 清理完成")
                
                # 重新检查
                can_generate, reason = MatchRuleManager.can_generate_games(match)
                print(f"🔍 重新检查: {'✅ 可以' if can_generate else '❌ 不可以'}")
        
        if not can_generate:
            print(f"❌ 无法继续测试: {reason}")
            return
        
        # 4. 测试参数验证
        print(f"\n🧮 参数验证测试:")
        try:
            rule = TotalRandomDouble(match)
            rule.validate_parameters()
            print("✅ 参数验证通过")
        except MatchRuleError as e:
            print(f"❌ 参数验证失败: {e}")
            print("\n💡 调整参数以满足要求...")
            
            # 自动调整参数
            participant_count = len(match.participants)
            print(f"   当前参与者: {participant_count} 人")
            
            # 计算合适的场地数 (假设每场地4人)
            ideal_court_count = max(1, participant_count // 4)
            needed_participants = ideal_court_count * 4
            
            print(f"   建议场地数: {ideal_court_count}")
            print(f"   需要参与者: {needed_participants} 人")
            
            if participant_count < needed_participants:
                print(f"   ⚠️  参与者不足，需要再添加 {needed_participants - participant_count} 人")
                return
            elif participant_count > needed_participants:
                print(f"   ⚠️  参与者过多，将只使用前 {needed_participants} 人")
                # 临时调整参与者
                original_participants = list(match.participants)
                match.participants.clear()
                for participant in original_participants[:needed_participants]:
                    match.participants.append(participant)
                db.session.commit()
            
            # 更新赛事参数
            match.court_count = ideal_court_count
            db.session.commit()
            
            print(f"   ✅ 参数已调整: 场地数={match.court_count}, 参与者={len(match.participants)}")
        
        # 5. 生成对局表
        print(f"\n🚀 生成对局表...")
        try:
            games = auto_generate_games(match.id, 'total_random_double')
            print(f"✅ 成功生成 {len(games)} 场比赛")
        except MatchRuleError as e:
            print(f"❌ 生成失败: {e}")
            return
        
        # 6. 显示生成的对局表
        print(f"\n📊 对局表详情:")
        print("=" * 60)
        
        games_by_round = {}
        for game in games:
            round_key = f"Round {game.round_number}"
            if round_key not in games_by_round:
                games_by_round[round_key] = []
            games_by_round[round_key].append(game)
        
        total_games = 0
        for round_name, round_games in games_by_round.items():
            print(f"\n🔸 {round_name} ({len(round_games)} 场比赛):")
            for game in round_games:
                team1 = f"{game.player1.nickname} & {game.player2.nickname}"
                team2 = f"{game.player3.nickname} & {game.player4.nickname}"
                time_str = game.scheduled_time.strftime('%H:%M')
                print(f"   🏟️ {game.court} {time_str}: {team1:<20} VS {team2}")
                total_games += 1
        
        # 7. 验证结果
        print(f"\n✅ 验证结果:")
        print(f"   预期比赛数: {match.court_count} × {match.round_count} = {match.court_count * match.round_count}")
        print(f"   实际生成数: {total_games}")
        print(f"   参与者数量: {len(match.participants)} 人")
        print(f"   每场比赛: 4 人 (双打)")
        print(f"   验证: {'✅ 正确' if total_games == match.court_count * match.round_count else '❌ 错误'}")
        
        # 8. 分组分析
        print(f"\n👥 分组分析:")
        rule = TotalRandomDouble(match)
        rule.validate_parameters()
        group_a, group_b = rule._divide_into_groups()
        
        print(f"   A组 ({len(group_a)} 人):")
        for player in group_a:
            print(f"      {player.nickname} (Rating: {player.rating})")
        
        print(f"   B组 ({len(group_b)} 人):")
        for player in group_b:
            print(f"      {player.nickname} (Rating: {player.rating})")
        
        avg_rating_a = sum(p.rating for p in group_a) / len(group_a) if group_a else 0
        avg_rating_b = sum(p.rating for p in group_b) / len(group_b) if group_b else 0
        print(f"   A组平均积分: {avg_rating_a:.1f}")
        print(f"   B组平均积分: {avg_rating_b:.1f}")
        print(f"   积分差异: {abs(avg_rating_a - avg_rating_b):.1f}")


def test_rule_validation():
    """测试规则验证功能"""
    app = create_app()
    
    with app.app_context():
        print("\n🧪 测试规则验证功能")
        print("=" * 40)
        
        match = Match.query.first()
        if not match:
            print("❌ 没有可测试的赛事")
            return
        
        # 测试不同的错误情况
        test_cases = [
            {"court_count": 0, "participants": 8, "expected": "场地数量必须大于0"},
            {"court_count": 2, "participants": 7, "expected": "参与人数错误"},
            {"court_count": 2, "participants": 9, "expected": "参与人数必须为偶数"},
        ]
        
        original_court_count = match.court_count
        original_participants = list(match.participants)
        
        for i, case in enumerate(test_cases, 1):
            print(f"\n测试用例 {i}: 场地={case['court_count']}, 参与者={case['participants']}")
            
            # 设置测试参数
            match.court_count = case['court_count']
            
            # 调整参与者数量
            match.participants.clear()
            for j in range(min(case['participants'], len(original_participants))):
                match.participants.append(original_participants[j])
            
            # 测试验证
            try:
                rule = TotalRandomDouble(match)
                rule.validate_parameters()
                print("   ❌ 应该抛出异常但没有")
            except MatchRuleError as e:
                expected = case['expected']
                if expected in str(e):
                    print(f"   ✅ 正确捕获异常: {e}")
                else:
                    print(f"   ⚠️  异常不匹配: {e}")
        
        # 恢复原始状态
        match.court_count = original_court_count
        match.participants.clear()
        for participant in original_participants:
            match.participants.append(participant)


if __name__ == '__main__':
    print("🎾 LaOpen 比赛规则系统测试")
    print("测试 TotalRandomDouble 规则...")
    print()
    
    # 运行主测试
    test_match_rule()
    
    # 运行验证测试
    test_rule_validation()
    
    print("\n🎉 测试完成！")
