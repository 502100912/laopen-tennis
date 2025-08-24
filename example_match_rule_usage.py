#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
比赛规则系统使用示例
展示如何在实际应用中使用 match_rule.py
"""

from app import create_app
from models import db, Match, Game
from match_rule import auto_generate_games, MatchRuleManager, MatchRuleError

def example_generate_games_for_match():
    """示例：为赛事生成对局表"""
    app = create_app()
    
    with app.app_context():
        print("🎯 示例：为赛事生成对局表")
        print("=" * 40)
        
        # 1. 获取赛事
        match = Match.query.filter_by(name='Spring Tennis Championship 2024').first()
        if not match:
            print("❌ 找不到赛事")
            return
        
        print(f"📋 赛事: {match.name}")
        print(f"👥 参与者: {len(match.participants)} 人")
        print(f"🏟️ 场地: {match.court_count} 个")
        print(f"🔄 轮数: {match.round_count} 轮")
        
        # 2. 检查是否可以生成
        can_generate, reason = MatchRuleManager.can_generate_games(match)
        if not can_generate:
            print(f"⚠️ 无法生成: {reason}")
            # 清理现有数据
            if "已有" in reason:
                Game.query.filter_by(match_id=match.id).delete()
                db.session.commit()
                print("🧹 已清理现有比赛数据")
        
        # 3. 生成对局表
        try:
            print("\n🚀 开始生成对局表...")
            games = auto_generate_games(match.id, 'total_random_double')
            print(f"✅ 成功生成 {len(games)} 场比赛")
            
            # 4. 展示结果
            print(f"\n📊 生成的对局表:")
            for game in games[:3]:  # 只显示前3场
                team1 = f"{game.player1.nickname} & {game.player2.nickname}"
                team2 = f"{game.player3.nickname} & {game.player4.nickname}"
                time_str = game.scheduled_time.strftime('%m/%d %H:%M')
                print(f"   🏟️ {game.court} {time_str}: {team1} VS {team2}")
            
            if len(games) > 3:
                print(f"   ... 以及其他 {len(games) - 3} 场比赛")
                
        except MatchRuleError as e:
            print(f"❌ 生成失败: {e}")

def example_integration_with_web():
    """示例：在Web应用中集成比赛规则系统"""
    print("\n🌐 示例：在Web应用中集成")
    print("=" * 40)
    
    # 这是一个概念性的代码示例，展示如何在Flask路由中使用
    code_example = '''
# 在 match_management.py 中添加新路由

@match_mgmt_bp.route('/<int:match_id>/generate_games', methods=['POST'])
@login_required
def generate_games(match_id):
    """为赛事生成对局表"""
    match = Match.query.get_or_404(match_id)
    
    # 检查权限（只有创建者或管理员可以生成）
    if match.created_by != current_user.id and not current_user.is_admin:
        flash('Only match creator can generate games', 'error')
        return redirect(url_for('match_mgmt.match_detail', match_id=match_id))
    
    # 检查是否可以生成
    can_generate, reason = MatchRuleManager.can_generate_games(match)
    if not can_generate:
        flash(f'Cannot generate games: {reason}', 'error')
        return redirect(url_for('match_mgmt.match_detail', match_id=match_id))
    
    try:
        # 生成对局表
        rule_type = request.form.get('rule_type', 'total_random_double')
        games = auto_generate_games(match_id, rule_type)
        
        flash(f'Successfully generated {len(games)} games!', 'success')
        
        # 更新赛事状态
        match.status = 'ongoing'
        db.session.commit()
        
    except MatchRuleError as e:
        flash(f'Failed to generate games: {str(e)}', 'error')
    
    return redirect(url_for('match_mgmt.match_detail', match_id=match_id))
    '''
    
    print("💡 Web集成代码示例:")
    print(code_example)

def example_custom_rule():
    """示例：如何创建自定义比赛规则"""
    print("\n🛠️ 示例：创建自定义比赛规则")
    print("=" * 40)
    
    custom_rule_example = '''
# 创建自定义比赛规则类

class KnockoutSingle(BaseMatchRule):
    """单打淘汰赛规则"""
    
    def validate_parameters(self):
        participant_count = len(self.participants)
        
        # 检查参与人数是否为2的幂次（便于淘汰赛）
        if participant_count & (participant_count - 1) != 0:
            raise MatchRuleError(f"淘汰赛参与人数必须为2的幂次（8,16,32...），实际{participant_count}人")
        
        return True
    
    def generate_games(self):
        self.validate_parameters()
        
        games = []
        participants = list(self.participants)
        round_num = 1
        
        while len(participants) > 1:
            round_games = []
            new_participants = []
            
            # 两两配对
            for i in range(0, len(participants), 2):
                if i + 1 < len(participants):
                    game = Game(
                        match_id=self.match.id,
                        game_type='singles',
                        round_name=f'Round {round_num}',
                        round_number=round_num,
                        player1_id=participants[i].id,
                        player3_id=participants[i+1].id,
                        status='scheduled'
                    )
                    round_games.append(game)
                    # 假设player1获胜进入下一轮
                    new_participants.append(participants[i])
            
            games.extend(round_games)
            participants = new_participants
            round_num += 1
        
        return games

# 在 MatchRuleManager 中注册新规则
MatchRuleManager.RULE_TYPES['knockout_single'] = KnockoutSingle
    '''
    
    print("💡 自定义规则代码示例:")
    print(custom_rule_example)

def example_best_practices():
    """示例：最佳实践建议"""
    print("\n📋 最佳实践建议")
    print("=" * 40)
    
    practices = [
        "🔍 生成对局表前总是先验证参数",
        "🧹 如有必要，先清理现有比赛数据", 
        "⚡ 使用事务确保数据一致性",
        "📊 记录操作日志便于调试",
        "🔐 检查用户权限（只有创建者可生成）",
        "📅 合理安排比赛时间间隔",
        "🏟️ 考虑场地可用性和冲突",
        "👥 平衡分组确保比赛公平性",
        "🎯 根据实际需要选择合适的规则类型",
        "📝 提供清晰的错误消息给用户"
    ]
    
    for practice in practices:
        print(f"   {practice}")

if __name__ == '__main__':
    print("🎾 LaOpen 比赛规则系统使用示例")
    print()
    
    # 运行所有示例
    example_generate_games_for_match()
    example_integration_with_web()
    example_custom_rule()
    example_best_practices()
    
    print("\n🎉 示例完成！")
    print("\n💡 要在你的应用中使用，只需：")
    print("   from match_rule import auto_generate_games")
    print("   games = auto_generate_games(match_id, 'total_random_double')")
