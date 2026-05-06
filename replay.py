import json
import os
from typing import List, Dict
from datetime import datetime
from physics import Vector3

class ReplayFrame:
    """Single frame of a replay"""
    def __init__(self, frame_number: int, timestamp: float):
        self.frame_number = frame_number
        self.timestamp = timestamp
        self.ball_pos = (0, 0, 0)
        self.ball_vel = (0, 0, 0)
        self.players = {}  # {player_id: {'pos': (x,y,z), 'vel': (x,y,z), 'boost': 0-100}}
        self.scores = {0: 0, 1: 0}
        self.events = []  # list of events this frame

class ReplayRecorder:
    """Records game replays"""
    def __init__(self, replay_name: str = None):
        self.replay_name = replay_name or f"replay_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.frames: List[ReplayFrame] = []
        self.events: List[Dict] = []
        self.start_time = datetime.now()
        self.frame_count = 0
    
    def record_frame(self, ball, players: List, scores: Dict) -> None:
        """Record a game frame"""
        timestamp = (datetime.now() - self.start_time).total_seconds()
        frame = ReplayFrame(self.frame_count, timestamp)
        
        # Record ball state
        frame.ball_pos = ball.position.to_tuple()
        frame.ball_vel = ball.velocity.to_tuple()
        
        # Record player states
        for i, player in enumerate(players):
            frame.players[i] = {
                'pos': player.position.to_tuple(),
                'vel': player.velocity.to_tuple(),
                'boost': player.boost_amount,
                'team': player.team
            }
        
        frame.scores = scores.copy()
        self.frames.append(frame)
        self.frame_count += 1
    
    def record_event(self, event_type: str, player_id: int, data: Dict = None) -> None:
        """Record a game event"""
        timestamp = (datetime.now() - self.start_time).total_seconds()
        event = {
            'timestamp': timestamp,
            'type': event_type,
            'player_id': player_id,
            'data': data or {}
        }
        self.events.append(event)
    
    def save_replay(self, directory: str = 'replays') -> str:
        """Save replay to file"""
        os.makedirs(directory, exist_ok=True)
        
        replay_data = {
            'name': self.replay_name,
            'created': self.start_time.isoformat(),
            'duration': (datetime.now() - self.start_time).total_seconds(),
            'frame_count': self.frame_count,
            'frames': [{
                'frame': f.frame_number,
                'timestamp': f.timestamp,
                'ball': {'pos': f.ball_pos, 'vel': f.ball_vel},
                'players': f.players,
                'scores': f.scores,
                'events': f.events
            } for f in self.frames],
            'events': self.events
        }
        
        filepath = os.path.join(directory, f"{self.replay_name}.json")
        with open(filepath, 'w') as f:
            json.dump(replay_data, f, indent=2)
        
        return filepath

class ReplayAnalyzer:
    """Analyzes recorded replays"""
    def __init__(self, replay_file: str):
        self.replay_file = replay_file
        self.replay_data = None
        self._load_replay()
    
    def _load_replay(self) -> None:
        """Load replay from file"""
        with open(self.replay_file, 'r') as f:
            self.replay_data = json.load(f)
    
    def get_summary(self) -> Dict:
        """Get replay summary"""
        return {
            'name': self.replay_data['name'],
            'created': self.replay_data['created'],
            'duration': self.replay_data['duration'],
            'total_frames': self.replay_data['frame_count']
        }
    
    def analyze_goals(self) -> List[Dict]:
        """Analyze all goals in replay"""
        goals = []
        prev_scores = {0: 0, 1: 0}
        
        for frame in self.replay_data['frames']:
            current_scores = frame['scores']
            
            for team in [0, 1]:
                if current_scores[team] > prev_scores[team]:
                    goal = {
                        'team': team,
                        'timestamp': frame['timestamp'],
                        'frame': frame['frame'],
                        'ball_pos': frame['ball']['pos']
                    }
                    goals.append(goal)
            
            prev_scores = current_scores
        
        return goals
    
    def analyze_player_stats(self, player_id: int) -> Dict:
        """Analyze specific player stats from replay"""
        total_distance = 0.0
        max_speed = 0.0
        aerial_time = 0.0
        boost_used = 0.0
        prev_boost = 100.0
        
        prev_pos = None
        
        for frame in self.replay_data['frames']:
            if str(player_id) in frame['players']:
                player = frame['players'][str(player_id)]
                pos = tuple(player['pos'])
                
                # Calculate distance traveled
                if prev_pos:
                    dx = pos[0] - prev_pos[0]
                    dy = pos[1] - prev_pos[1]
                    dz = pos[2] - prev_pos[2]
                    distance = (dx**2 + dy**2 + dz**2)**0.5
                    total_distance += distance
                
                # Track aerial time
                if pos[1] > 2.0:  # above ground radius
                    aerial_time += 1/60  # assume 60fps
                
                # Track boost usage
                current_boost = player['boost']
                if current_boost < prev_boost:
                    boost_used += prev_boost - current_boost
                prev_boost = current_boost
                
                prev_pos = pos
        
        return {
            'player_id': player_id,
            'total_distance': total_distance,
            'aerial_time': aerial_time,
            'boost_used': boost_used
        }
    
    def get_ball_statistics(self) -> Dict:
        """Analyze ball movement statistics"""
        speeds = []
        max_height = 0.0
        
        for frame in self.replay_data['frames']:
            pos = frame['ball']['pos']
            vel = frame['ball']['vel']
            
            # Calculate speed
            speed = (vel[0]**2 + vel[1]**2 + vel[2]**2)**0.5
            speeds.append(speed)
            
            # Track max height
            max_height = max(max_height, pos[1])
        
        avg_speed = sum(speeds) / len(speeds) if speeds else 0
        max_speed = max(speeds) if speeds else 0
        
        return {
            'average_speed': avg_speed,
            'max_speed': max_speed,
            'max_height': max_height
        }
