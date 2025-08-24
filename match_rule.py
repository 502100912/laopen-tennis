#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LaOpen 比赛规则管理系统
为不同类型的比赛生成自动对局表
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from models import db, Match, Game, User


class MatchRuleError(Exception):
    """比赛规则异常"""
    pass


class BaseMatchRule:
    """比赛规则基类"""
    
    def __init__(self, match: Match):
        self.match = match
        self.participants = list(match.participants)
        
    def validate_parameters(self) -> bool:
        """验证比赛参数"""
        raise NotImplementedError("子类必须实现此方法")
    
    def generate_games(self) -> List[Game]:
        """生成比赛对局"""
        raise NotImplementedError("子类必须实现此方法")


class TotalRandomDouble(BaseMatchRule):
    """
    完全随机双打比赛规则
    - 将参赛选手分为a、b两组
    - 组内随机组队并互相对阵
    - 适用于友谊赛和练习赛
    """
    
    def __init__(self, match: Match):
        super().__init__(match)
        self.group_a = []
        self.group_b = []
        
    def validate_parameters(self) -> bool:
        """
        验证比赛参数
        - 参赛选手数量必须 = court_count * 4
        - 必须是偶数，以便分为两组
        """
        participant_count = len(self.participants)
        required_count = self.match.court_count * 4
        
        # 检查参与人数
        if participant_count != required_count:
            raise MatchRuleError(
                f"参与人数错误：需要 {required_count} 人 (场地数 {self.match.court_count} × 4)，"
                f"实际 {participant_count} 人"
            )
        
        # 检查是否为偶数（可以分为两组）
        if participant_count % 2 != 0:
            raise MatchRuleError(f"参与人数必须为偶数，实际 {participant_count} 人")
        
        # 检查场地数量和轮数
        if self.match.court_count <= 0:
            raise MatchRuleError(f"场地数量必须大于0，实际 {self.match.court_count}")
        
        if self.match.round_count <= 0:
            raise MatchRuleError(f"比赛轮数必须大于0，实际 {self.match.round_count}")
        
        return True
    
    def _divide_into_groups(self) -> Tuple[List[User], List[User]]:
        """
        将参赛选手按照积分分为两组
        高积分和低积分选手平衡分配
        """
        # 按积分排序
        sorted_participants = sorted(self.participants, key=lambda x: x.rating, reverse=True)
        
        group_a = []
        group_b = []
        
        # 蛇形分组：1,4,5,8,9... → A组，2,3,6,7,10... → B组
        for i, player in enumerate(sorted_participants):
            if (i // 2) % 2 == 0:
                group_a.append(player)
            else:
                group_b.append(player)
        
        self.group_a = group_a
        self.group_b = group_b
        
        return group_a, group_b
    
    def _create_random_pairs(self, round_num: int) -> List[Tuple[User, User, User, User]]:
        """
        为每轮比赛创建随机配对
        返回: [(player1, player2, player3, player4), ...] 
        其中 player1,2 为A组队友，player3,4 为B组队友
        """
        # 每轮比赛都重新随机分组
        shuffled_a = self.group_a.copy()
        shuffled_b = self.group_b.copy()
        random.shuffle(shuffled_a)
        random.shuffle(shuffled_b)
        
        pairings = []
        players_per_court = 4  # 双打每场地4人
        
        for court_idx in range(self.match.court_count):
            start_idx = court_idx * 2  # 每场地从A、B组各取2人
            
            # 确保有足够的选手
            if start_idx + 1 >= len(shuffled_a) or start_idx + 1 >= len(shuffled_b):
                break
                
            player1 = shuffled_a[start_idx]      # A组队友1
            player2 = shuffled_a[start_idx + 1]  # A组队友2
            player3 = shuffled_b[start_idx]      # B组队友1
            player4 = shuffled_b[start_idx + 1]  # B组队友2
            
            pairings.append((player1, player2, player3, player4))
        
        return pairings
    
    def generate_games(self) -> List[Game]:
        """
        生成比赛对局表
        返回所有生成的Game对象列表
        """
        # 验证参数
        self.validate_parameters()
        
        # 分组
        self._divide_into_groups()
        
        print(f"🎾 开始生成 {self.match.name} 的对局表")
        print(f"📊 参数: {self.match.court_count}场地 × {self.match.round_count}轮 = {self.match.court_count * self.match.round_count}场比赛")
        print(f"👥 分组: A组 {len(self.group_a)} 人，B组 {len(self.group_b)} 人")
        
        generated_games = []
        
        # 生成比赛开始时间
        base_time = self.match.start_datetime
        
        for round_num in range(1, self.match.round_count + 1):
            print(f"\n🔸 第 {round_num} 轮:")
            
            # 为本轮创建随机配对
            pairings = self._create_random_pairs(round_num)
            
            for court_idx, (player1, player2, player3, player4) in enumerate(pairings):
                # 计算比赛时间（每轮间隔2小时，同轮不同场地同时进行）
                game_time = base_time + timedelta(hours=(round_num - 1) * 2)
                
                # 创建Game对象
                game = Game(
                    match_id=self.match.id,
                    game_type='doubles',
                    round_name=f'Round {round_num}',
                    round_number=round_num,
                    
                    # 双打队伍设置
                    player1_id=player1.id,  # A组队友1
                    player2_id=player2.id,  # A组队友2  
                    player3_id=player3.id,  # B组队友1
                    player4_id=player4.id,  # B组队友2
                    
                    # 比赛安排
                    scheduled_time=game_time,
                    court=f"Court {chr(65 + court_idx)}",  # Court A, B, C...
                    status='scheduled',
                    
                    # 初始比分
                    winner_team=0,
                    set1_team1_score=0,
                    set1_team2_score=0,
                    set2_team1_score=0,
                    set2_team2_score=0,
                    set3_team1_score=0,
                    set3_team2_score=0,
                    
                    # 备注
                    notes=f"Random doubles pairing - Round {round_num}"
                )
                
                generated_games.append(game)
                
                print(f"  🏟️ {game.court}: {player1.nickname}&{player2.nickname} VS {player3.nickname}&{player4.nickname}")
                print(f"     ⏰ {game_time.strftime('%Y-%m-%d %H:%M')}")
        
        print(f"\n✅ 生成完成！共创建 {len(generated_games)} 场比赛")
        
        return generated_games


class MatchRuleManager:
    """比赛规则管理器"""
    
    # 可用的比赛规则类型
    RULE_TYPES = {
        'total_random_double': TotalRandomDouble,
        # 可以添加更多规则类型
        # 'knockout_single': KnockoutSingle,
        # 'round_robin': RoundRobin,
    }
    
    @classmethod
    def get_rule_class(cls, rule_type: str) -> Optional[type]:
        """获取规则类"""
        return cls.RULE_TYPES.get(rule_type)
    
    @classmethod
    def generate_games_for_match(cls, match: Match, rule_type: str = 'total_random_double') -> List[Game]:
        """
        为指定赛事生成比赛对局
        
        Args:
            match: 赛事对象
            rule_type: 规则类型
            
        Returns:
            生成的Game对象列表
        """
        rule_class = cls.get_rule_class(rule_type)
        if not rule_class:
            raise MatchRuleError(f"不支持的比赛规则类型: {rule_type}")
        
        # 创建规则实例并生成对局
        rule_instance = rule_class(match)
        games = rule_instance.generate_games()
        
        # 保存到数据库
        for game in games:
            db.session.add(game)
        
        try:
            db.session.commit()
            print(f"💾 成功保存 {len(games)} 场比赛到数据库")
        except Exception as e:
            db.session.rollback()
            raise MatchRuleError(f"保存比赛数据失败: {str(e)}")
        
        return games
    
    @classmethod
    def can_generate_games(cls, match: Match) -> Tuple[bool, str]:
        """
        检查赛事是否可以生成对局表
        
        Returns:
            (可以生成, 原因说明)
        """
        # 检查赛事状态
        if match.status not in ['preparing', 'registering']:
            return False, f"赛事状态错误：{match.status}，只有 preparing 或 registering 状态可以生成对局表"
        
        # 检查是否已有比赛
        existing_games = Game.query.filter_by(match_id=match.id).count()
        if existing_games > 0:
            return False, f"该赛事已有 {existing_games} 场比赛，请先清除现有对局表"
        
        # 检查参与人数
        if len(match.participants) == 0:
            return False, "没有参与者"
        
        return True, "可以生成对局表"


# 便捷函数
def auto_generate_games(match_id: int, rule_type: str = 'total_random_double') -> List[Game]:
    """
    为指定赛事ID自动生成对局表的便捷函数
    
    Args:
        match_id: 赛事ID
        rule_type: 比赛规则类型
        
    Returns:
        生成的Game对象列表
    """
    match = Match.query.get_or_404(match_id)
    
    # 检查是否可以生成
    can_generate, reason = MatchRuleManager.can_generate_games(match)
    if not can_generate:
        raise MatchRuleError(reason)
    
    # 生成对局表
    return MatchRuleManager.generate_games_for_match(match, rule_type)


if __name__ == '__main__':
    # 测试代码
    print("🎾 比赛规则系统测试")
    print("请在Flask应用上下文中运行具体的测试")
