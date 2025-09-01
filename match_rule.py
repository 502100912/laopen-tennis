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
    
    def __init__(self, match: Match, predefined_groups=None):
        super().__init__(match)
        self.group_a = []
        self.group_b = []
        # 简洁的历史记录：每个选手的队友和对手ID集合
        self.teammate_history = {}  # {user_id: set(teammate_ids)}
        self.opponent_history = {}  # {user_id: set(opponent_ids)}
        
        # 如果有预定义分组，使用预定义分组，否则按积分自动分组
        if predefined_groups:
            self.group_a, self.group_b = predefined_groups
            print("📌 使用预定义分组：A组{}人，B组{}人".format(len(self.group_a), len(self.group_b)))
        else:
            self._divide_into_groups()
            print("📊 自动按积分分组：A组{}人，B组{}人".format(len(self.group_a), len(self.group_b)))
        
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
                "参与人数错误：需要 {} 人 (场地数 {} × 4)，实际 {} 人".format(required_count, self.match.court_count, participant_count)
            )
        
        # 检查是否为偶数（可以分为两组）
        if participant_count % 2 != 0:
            raise MatchRuleError("参与人数必须为偶数，实际 {} 人".format(participant_count))
        
        # 检查场地数量和轮数
        if self.match.court_count <= 0:
            raise MatchRuleError("场地数量必须大于0，实际 {}".format(self.match.court_count))
        
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
    
    def _init_history(self):
        """初始化历史记录"""
        for user in self.participants:
            self.teammate_history[user.id] = set()
            self.opponent_history[user.id] = set()
    
    def _calculate_conflict_score(self, pairing):
        """计算配对的冲突分数（越低越好）"""
        p1, p2, p3, p4 = pairing
        score = 0
        
        # 队友重复惩罚（权重2）
        if p2.id in self.teammate_history[p1.id]:
            score += 2
        if p4.id in self.teammate_history[p3.id]:
            score += 2
            
        # 对手重复惩罚（权重1）  
        for a_player in [p1, p2]:
            for b_player in [p3, p4]:
                if b_player.id in self.opponent_history[a_player.id]:
                    score += 1
        
        return score
    
    def _update_history(self, pairings):
        """更新历史记录"""
        for p1, p2, p3, p4 in pairings:
            # 更新队友历史
            self.teammate_history[p1.id].add(p2.id)
            self.teammate_history[p2.id].add(p1.id)
            self.teammate_history[p3.id].add(p4.id)
            self.teammate_history[p4.id].add(p3.id)
            
            # 更新对手历史
            for a in [p1, p2]:
                for b in [p3, p4]:
                    self.opponent_history[a.id].add(b.id)
                    self.opponent_history[b.id].add(a.id)
    
    def _create_random_pairs(self, round_num: int) -> List[Tuple[User, User, User, User]]:
        """
        智能配对算法：尽量避免重复队友和对手
        返回: [(player1, player2, player3, player4), ...] 
        """
        if round_num == 1:
            self._init_history()
        
        print(f"  🎯 第{round_num}轮智能配对:")
        
        # 简单策略：尝试多种随机排列，选择冲突最小的
        best_pairings = None
        best_score = float('inf')
        
        for attempt in range(50):  # 尝试50种排列
            shuffled_a = self.group_a.copy()
            shuffled_b = self.group_b.copy()
            random.shuffle(shuffled_a)
            random.shuffle(shuffled_b)
            
            # 生成本次尝试的配对
            current_pairings = []
            for court_idx in range(self.match.court_count):
                start_idx = court_idx * 2
                if start_idx + 1 >= len(shuffled_a) or start_idx + 1 >= len(shuffled_b):
                    break
                
                pairing = (
                    shuffled_a[start_idx],
                    shuffled_a[start_idx + 1],
                    shuffled_b[start_idx],
                    shuffled_b[start_idx + 1]
                )
                current_pairings.append(pairing)
            
            # 计算总冲突分数
            total_score = sum(self._calculate_conflict_score(p) for p in current_pairings)
            
            # 更新最佳方案
            if total_score < best_score:
                best_score = total_score
                best_pairings = current_pairings
                if total_score == 0:  # 完美方案，提前退出
                    break
        
        # 输出配对结果
        for idx, (p1, p2, p3, p4) in enumerate(best_pairings):
            court = chr(65 + idx)  # A, B, C...
            conflict = self._calculate_conflict_score((p1, p2, p3, p4))
            print(f"     Court {court}: {p1.nickname}+{p2.nickname} VS {p3.nickname}+{p4.nickname} (冲突:{conflict})")
        
        print(f"     📊 总冲突分数: {best_score}")
        
        # 更新历史记录
        self._update_history(best_pairings)
        
        return best_pairings
    
    def _get_court_name(self, court_idx):
        """获取场地名称"""
        courts = self.match.get_courts()
        if courts and court_idx < len(courts):
            return f"场地 {courts[court_idx]}"
        else:
            return f"Court {chr(65 + court_idx)}"  # 默认 Court A, B, C...
    
    def _show_final_stats(self):
        """显示最终的多样性统计"""
        print(f"\n  📊 配对多样性统计:")
        
        total_teammate_diversity = 0
        total_opponent_diversity = 0
        
        for user in self.participants:
            # 计算可能的队友和对手数
            if user in self.group_a:
                max_teammates = len(self.group_a) - 1
                max_opponents = len(self.group_b)
            else:
                max_teammates = len(self.group_b) - 1
                max_opponents = len(self.group_a)
            
            actual_teammates = len(self.teammate_history.get(user.id, set()))
            actual_opponents = len(self.opponent_history.get(user.id, set()))
            
            teammate_ratio = actual_teammates / max_teammates * 100 if max_teammates > 0 else 0
            opponent_ratio = actual_opponents / max_opponents * 100 if max_opponents > 0 else 0
            
            total_teammate_diversity += teammate_ratio
            total_opponent_diversity += opponent_ratio
        
        avg_teammate = total_teammate_diversity / len(self.participants)
        avg_opponent = total_opponent_diversity / len(self.participants)
        
        print(f"     🤝 平均队友多样性: {avg_teammate:.1f}%")
        print(f"     ⚔️ 平均对手多样性: {avg_opponent:.1f}%")
        
        # 计算完美程度
        perfect_score = (avg_teammate + avg_opponent) / 2
        if perfect_score >= 90:
            print(f"     🎉 配对质量: 优秀 ({perfect_score:.1f}%)")
        elif perfect_score >= 70:
            print(f"     ✨ 配对质量: 良好 ({perfect_score:.1f}%)")
        else:
            print(f"     📈 配对质量: 一般 ({perfect_score:.1f}%)")
    
    def generate_games(self) -> List[Game]:
        """
        生成比赛对局表
        返回所有生成的Game对象列表
        """
        # 验证参数
        self.validate_parameters()
        
        # 分组（如果构造函数中没有使用预定义分组，则按积分自动分组）
        if not (self.group_a and self.group_b):
            self._divide_into_groups()
        
        print(f"🎾 开始生成 {self.match.name} 的对局表")
        print(f"📊 参数: {self.match.court_count}场地 × {self.match.round_count}轮 = {self.match.court_count * self.match.round_count}场比赛")
        print(f"👥 分组: A组 {len(self.group_a)} 人，B组 {len(self.group_b)} 人")
        
        # 显示详细分组信息
        print(f"\n🔸 A组成员: {', '.join([p.nickname for p in self.group_a])}")
        print(f"🔸 B组成员: {', '.join([p.nickname for p in self.group_b])}")
        
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
                    court=self._get_court_name(court_idx),
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
        
        # 显示最终统计
        self._show_final_stats()
        
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
    def generate_games_for_match(cls, match: Match, rule_type: str = 'total_random_double', predefined_groups=None) -> List[Game]:
        """
        为指定赛事生成比赛对局
        
        Args:
            match: 赛事对象
            rule_type: 规则类型
            predefined_groups: 预定义分组 (group_a, group_b) 的元组
            
        Returns:
            生成的Game对象列表
        """
        rule_class = cls.get_rule_class(rule_type)
        if not rule_class:
            raise MatchRuleError(f"不支持的比赛规则类型: {rule_type}")
        
        # 创建规则实例并生成对局
        # 如果有预定义分组，传递给规则实例
        if predefined_groups and rule_type == 'total_random_double':
            rule_instance = rule_class(match, predefined_groups)
        else:
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
def auto_generate_games(match_id: int, rule_type: str = 'total_random_double', predefined_groups=None) -> List[Game]:
    """
    为指定赛事ID自动生成对局表的便捷函数
    
    Args:
        match_id: 赛事ID
        rule_type: 比赛规则类型
        predefined_groups: 预定义分组 (group_a, group_b) 的元组，如果提供则跳过自动分组
        
    Returns:
        生成的Game对象列表
    """
    match = Match.query.get_or_404(match_id)
    
    # 检查是否可以生成
    can_generate, reason = MatchRuleManager.can_generate_games(match)
    if not can_generate:
        raise MatchRuleError(reason)
    
    # 生成对局表
    return MatchRuleManager.generate_games_for_match(match, rule_type, predefined_groups)


class MatchupGenerator:
    """
    对阵表生成器
    用于生成简单的对阵表，不涉及数据库存储
    支持多样性匹配，避免重复队友和对手
    """
    
    def __init__(self):
        # 历史记录：避免重复配对
        self.teammate_history = {}  # {player_name: set(teammate_names)}
        self.opponent_history = {}  # {player_name: set(opponent_names)}
    
    def generate_team_matchups(self, match_format: str, group_a: List[str], group_b: List[str], 
                              court_names: List[str], rounds: int) -> Dict:
        """
        生成团队对阵表 (GroupA vs GroupB)
        
        Args:
            match_format: 比赛格式 (singles/doubles)
            group_a: A组参与者列表
            group_b: B组参与者列表
            court_names: 场地名称列表
            rounds: 轮次数量
            
        Returns:
            按轮次组织的对阵表字典
        """
        if len(group_a) < 2 or len(group_b) < 2:
            raise ValueError("Each group must have at least 2 players")
            
        # 初始化历史记录
        all_players = group_a + group_b
        self._init_history(all_players)
            
        matchups = {}
        
        for round_num in range(1, rounds + 1):
            round_matchups = []
            
            if match_format == 'singles':
                round_matchups = self._generate_team_singles_smart(group_a, group_b, court_names, round_num)
            else:  # doubles
                round_matchups = self._generate_team_doubles_smart(group_a, group_b, court_names, round_num)
                
            matchups[round_num] = round_matchups
            
        return matchups
    
    def generate_random_matchups(self, match_format: str, participants: List[str], 
                                court_names: List[str], rounds: int) -> Dict:
        """
        生成随机对阵表 (AllRandom)
        
        Args:
            match_format: 比赛格式 (singles/doubles)
            participants: 参与者姓名列表
            court_names: 场地名称列表
            rounds: 轮次数量
            
        Returns:
            按轮次组织的对阵表字典
        """
        if len(participants) < 4:
            raise ValueError("Number of participants must be at least 4")
        
        if match_format == 'singles' and len(participants) % 2 != 0:
            raise ValueError("Singles requires even number of participants")
        elif match_format == 'doubles' and len(participants) % 4 != 0:
            raise ValueError("Doubles requires participants divisible by 4")
            
        # 初始化历史记录
        self._init_history(participants)
            
        matchups = {}
        
        for round_num in range(1, rounds + 1):
            round_matchups = []
            
            if match_format == 'singles':
                round_matchups = self._generate_random_singles_smart(participants, court_names, round_num)
            else:  # doubles
                round_matchups = self._generate_random_doubles_smart(participants, court_names, round_num)
                
            matchups[round_num] = round_matchups
            
        return matchups
    
    def _init_history(self, participants: List[str]):
        """初始化历史记录"""
        for player in participants:
            self.teammate_history[player] = set()
            self.opponent_history[player] = set()
    
    def _calculate_conflict_score(self, matchup):
        """计算配对的冲突分数（越低越好）"""
        score = 0
        
        if len(matchup['team1']) == 2 and len(matchup['team2']) == 2:
            # 双打模式
            p1, p2 = matchup['team1']
            p3, p4 = matchup['team2']
            
            # 队友重复惩罚（权重2）
            if p2 in self.teammate_history[p1]:
                score += 2
            if p4 in self.teammate_history[p3]:
                score += 2
                
            # 对手重复惩罚（权重1）
            for a_player in [p1, p2]:
                for b_player in [p3, p4]:
                    if b_player in self.opponent_history[a_player]:
                        score += 1
        else:
            # 单打模式
            p1 = matchup['team1'][0]
            p2 = matchup['team2'][0]
            
            # 对手重复惩罚
            if p2 in self.opponent_history[p1]:
                score += 2
                
        return score
    
    def _update_history(self, round_matchups: List):
        """更新历史记录"""
        for matchup in round_matchups:
            if len(matchup['team1']) == 2 and len(matchup['team2']) == 2:
                # 双打模式
                p1, p2 = matchup['team1']
                p3, p4 = matchup['team2']
                
                # 更新队友历史
                self.teammate_history[p1].add(p2)
                self.teammate_history[p2].add(p1)
                self.teammate_history[p3].add(p4)
                self.teammate_history[p4].add(p3)
                
                # 更新对手历史
                for a in [p1, p2]:
                    for b in [p3, p4]:
                        self.opponent_history[a].add(b)
                        self.opponent_history[b].add(a)
            else:
                # 单打模式
                p1 = matchup['team1'][0]
                p2 = matchup['team2'][0]
                
                # 更新对手历史
                self.opponent_history[p1].add(p2)
                self.opponent_history[p2].add(p1)
    
    def _generate_team_singles(self, group_a: List[str], group_b: List[str], court_names: List[str]) -> List:
        """生成团队单打对阵 (GroupA vs GroupB)"""
        matchups = []
        court_index = 0
        
        # 打乱两组的顺序
        shuffled_a = group_a.copy()
        shuffled_b = group_b.copy()
        random.shuffle(shuffled_a)
        random.shuffle(shuffled_b)
        
        # 配对A组和B组选手
        min_len = min(len(shuffled_a), len(shuffled_b))
        for i in range(min_len):
            matchup = {
                'team1': [shuffled_a[i]],
                'team2': [shuffled_b[i]],
                'court': court_names[court_index % len(court_names)]
            }
            matchups.append(matchup)
            court_index += 1
                
        return matchups
    
    def _generate_team_doubles(self, group_a: List[str], group_b: List[str], court_names: List[str]) -> List:
        """生成团队双打对阵 (GroupA vs GroupB)"""
        matchups = []
        court_index = 0
        
        # 打乱两组的顺序
        shuffled_a = group_a.copy()
        shuffled_b = group_b.copy()
        random.shuffle(shuffled_a)
        random.shuffle(shuffled_b)
        
        # 确保每组至少有2人可以组成双打
        a_pairs = len(shuffled_a) // 2
        b_pairs = len(shuffled_b) // 2
        max_pairs = min(a_pairs, b_pairs)
        
        for i in range(max_pairs):
            team_a = [shuffled_a[i*2], shuffled_a[i*2 + 1]]
            team_b = [shuffled_b[i*2], shuffled_b[i*2 + 1]]
            
            matchup = {
                'team1': team_a,
                'team2': team_b,
                'court': court_names[court_index % len(court_names)]
            }
            matchups.append(matchup)
            court_index += 1
                
        return matchups
    
    def _generate_random_singles(self, participants: List[str], court_names: List[str]) -> List:
        """生成完全随机单打对阵"""
        shuffled = participants.copy()
        random.shuffle(shuffled)
        
        matchups = []
        court_index = 0
        
        # 每2个人组成一场单打比赛
        for i in range(0, len(shuffled) - 1, 2):
            matchup = {
                'team1': [shuffled[i]],
                'team2': [shuffled[i + 1]],
                'court': court_names[court_index % len(court_names)]
            }
            matchups.append(matchup)
            court_index += 1
                    
        return matchups
    
    def _generate_random_doubles(self, participants: List[str], court_names: List[str]) -> List:
        """生成完全随机双打对阵"""
        shuffled = participants.copy()
        random.shuffle(shuffled)
        
        matchups = []
        court_index = 0
        
        # 每4个人组成一场双打比赛
        for i in range(0, len(shuffled) - 3, 4):
            team1 = [shuffled[i], shuffled[i + 1]]
            team2 = [shuffled[i + 2], shuffled[i + 3]]
            
            matchup = {
                'team1': team1,
                'team2': team2,
                'court': court_names[court_index % len(court_names)]
            }
            matchups.append(matchup)
            court_index += 1
                
        return matchups
    
    def _generate_team_singles_smart(self, group_a: List[str], group_b: List[str], court_names: List[str], round_num: int) -> List:
        """生成智能团队单打对阵 (GroupA vs GroupB)"""
        best_matchups = None
        best_score = float('inf')
        
        # 尝试多种组合，选择冲突最小的
        for attempt in range(30):
            shuffled_a = group_a.copy()
            shuffled_b = group_b.copy()
            random.shuffle(shuffled_a)
            random.shuffle(shuffled_b)
            
            current_matchups = []
            court_index = 0
            
            min_len = min(len(shuffled_a), len(shuffled_b))
            for i in range(min_len):
                if court_index >= len(court_names):
                    break
                    
                matchup = {
                    'team1': [shuffled_a[i]],
                    'team2': [shuffled_b[i]],
                    'court': court_names[court_index % len(court_names)]
                }
                current_matchups.append(matchup)
                court_index += 1
            
            # 计算总冲突分数
            total_score = sum(self._calculate_conflict_score(m) for m in current_matchups)
            
            if total_score < best_score:
                best_score = total_score
                best_matchups = current_matchups
                if total_score == 0:
                    break
        
        # 更新历史记录
        self._update_history(best_matchups)
        return best_matchups
    
    def _generate_team_doubles_smart(self, group_a: List[str], group_b: List[str], court_names: List[str], round_num: int) -> List:
        """生成智能团队双打对阵 (GroupA vs GroupB)"""
        best_matchups = None
        best_score = float('inf')
        
        # 尝试多种组合，选择冲突最小的
        for attempt in range(50):
            shuffled_a = group_a.copy()
            shuffled_b = group_b.copy()
            random.shuffle(shuffled_a)
            random.shuffle(shuffled_b)
            
            current_matchups = []
            court_index = 0
            
            a_pairs = len(shuffled_a) // 2
            b_pairs = len(shuffled_b) // 2
            max_pairs = min(a_pairs, b_pairs, len(court_names))
            
            for i in range(max_pairs):
                team_a = [shuffled_a[i*2], shuffled_a[i*2 + 1]]
                team_b = [shuffled_b[i*2], shuffled_b[i*2 + 1]]
                
                matchup = {
                    'team1': team_a,
                    'team2': team_b,
                    'court': court_names[court_index % len(court_names)]
                }
                current_matchups.append(matchup)
                court_index += 1
            
            # 计算总冲突分数
            total_score = sum(self._calculate_conflict_score(m) for m in current_matchups)
            
            if total_score < best_score:
                best_score = total_score
                best_matchups = current_matchups
                if total_score == 0:
                    break
        
        # 更新历史记录
        self._update_history(best_matchups)
        return best_matchups
    
    def _generate_random_singles_smart(self, participants: List[str], court_names: List[str], round_num: int) -> List:
        """生成智能随机单打对阵"""
        best_matchups = None
        best_score = float('inf')
        
        # 尝试多种组合，选择冲突最小的
        for attempt in range(30):
            shuffled = participants.copy()
            random.shuffle(shuffled)
            
            current_matchups = []
            court_index = 0
            
            for i in range(0, len(shuffled) - 1, 2):
                if court_index >= len(court_names):
                    break
                    
                matchup = {
                    'team1': [shuffled[i]],
                    'team2': [shuffled[i + 1]],
                    'court': court_names[court_index % len(court_names)]
                }
                current_matchups.append(matchup)
                court_index += 1
            
            # 计算总冲突分数
            total_score = sum(self._calculate_conflict_score(m) for m in current_matchups)
            
            if total_score < best_score:
                best_score = total_score
                best_matchups = current_matchups
                if total_score == 0:
                    break
        
        # 更新历史记录
        self._update_history(best_matchups)
        return best_matchups
    
    def _generate_random_doubles_smart(self, participants: List[str], court_names: List[str], round_num: int) -> List:
        """生成智能随机双打对阵"""
        best_matchups = None
        best_score = float('inf')
        
        # 尝试多种组合，选择冲突最小的
        for attempt in range(50):
            shuffled = participants.copy()
            random.shuffle(shuffled)
            
            current_matchups = []
            court_index = 0
            
            for i in range(0, len(shuffled) - 3, 4):
                if court_index >= len(court_names):
                    break
                    
                team1 = [shuffled[i], shuffled[i + 1]]
                team2 = [shuffled[i + 2], shuffled[i + 3]]
                
                matchup = {
                    'team1': team1,
                    'team2': team2,
                    'court': court_names[court_index % len(court_names)]
                }
                current_matchups.append(matchup)
                court_index += 1
            
            # 计算总冲突分数
            total_score = sum(self._calculate_conflict_score(m) for m in current_matchups)
            
            if total_score < best_score:
                best_score = total_score
                best_matchups = current_matchups
                if total_score == 0:
                    break
        
        # 更新历史记录
        self._update_history(best_matchups)
        return best_matchups


if __name__ == '__main__':
    # 测试代码
    print("🎾 比赛规则系统测试")
    print("请在Flask应用上下文中运行具体的测试")
