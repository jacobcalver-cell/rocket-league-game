from dataclasses import dataclass
from typing import List, Dict
from datetime import datetime

@dataclass
class Goal:
    """Represents a goal scored in the game"""
    team: int
    scorer: int  # player number
    time: float  # game time when goal was scored
    position: tuple  # (x, y, z) position where goal was scored
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class PlayerStats:
    """Track individual player statistics"""
    player_id: int
    team: int
    goals: int = 0
    assists: int = 0
    saves: int = 0
    shots: int = 0
    hits: int = 0
    aerial_goals: int = 0
    demolitions: int = 0
    aerial_time: float = 0.0  # seconds in the air
    boost_usage: float = 0.0  # boost consumed
    distance_traveled: float = 0.0
    average_speed: float = 0.0

class ScoringSystem:
    """Manages game scoring and statistics"""
    def __init__(self):
        self.goals: List[Goal] = []
        self.team_scores = {0: 0, 1: 0}  # blue and orange
        self.player_stats: Dict[int, PlayerStats] = {}
        self.game_start_time = datetime.now()
    
    def add_goal(self, team: int, scorer: int, time: float, position: tuple) -> None:
        """Record a goal"""
        goal = Goal(team=team, scorer=scorer, time=time, position=position)
        self.goals.append(goal)
        self.team_scores[team] += 1
        
        if scorer in self.player_stats:
            self.player_stats[scorer].goals += 1
    
    def add_player(self, player_id: int, team: int) -> None:
        """Add a player to track stats"""
        self.player_stats[player_id] = PlayerStats(player_id=player_id, team=team)
    
    def record_hit(self, player_id: int) -> None:
        """Record a ball hit by a player"""
        if player_id in self.player_stats:
            self.player_stats[player_id].hits += 1
    
    def record_save(self, player_id: int) -> None:
        """Record a save by a player"""
        if player_id in self.player_stats:
            self.player_stats[player_id].saves += 1
    
    def record_shot(self, player_id: int) -> None:
        """Record a shot by a player"""
        if player_id in self.player_stats:
            self.player_stats[player_id].shots += 1
    
    def update_player_distance(self, player_id: int, distance: float) -> None:
        """Update distance traveled by player"""
        if player_id in self.player_stats:
            self.player_stats[player_id].distance_traveled += distance
    
    def update_player_aerial_time(self, player_id: int, time: float) -> None:
        """Update aerial time for player"""
        if player_id in self.player_stats:
            self.player_stats[player_id].aerial_time += time
    
    def update_player_boost_usage(self, player_id: int, boost_used: float) -> None:
        """Update boost usage for player"""
        if player_id in self.player_stats:
            self.player_stats[player_id].boost_usage += boost_used
    
    def get_team_score(self, team: int) -> int:
        """Get team score"""
        return self.team_scores.get(team, 0)
    
    def get_player_stats(self, player_id: int) -> PlayerStats:
        """Get player statistics"""
        return self.player_stats.get(player_id)
    
    def get_game_summary(self) -> Dict:
        """Get summary of the game"""
        elapsed_time = (datetime.now() - self.game_start_time).total_seconds()
        return {
            'blue_score': self.team_scores[0],
            'orange_score': self.team_scores[1],
            'goals': [(g.team, g.scorer, g.time, g.position) for g in self.goals],
            'elapsed_time': elapsed_time,
            'player_stats': {pid: {
                'goals': ps.goals,
                'assists': ps.assists,
                'saves': ps.saves,
                'shots': ps.shots,
                'hits': ps.hits,
                'aerial_time': ps.aerial_time,
                'distance_traveled': ps.distance_traveled
            } for pid, ps in self.player_stats.items()}
        }
