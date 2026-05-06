import pygame
from typing import Dict, List, Tuple
from physics import Ball, Vector3
from player import Player
from scoring import ScoringSystem
from replay import ReplayRecorder, ReplayAnalyzer
import math

class RocketLeagueGame:
    """Main game logic and loop"""
    def __init__(self, width: int = 1600, height: int = 900, fps: int = 60):
        self.width = width
        self.height = height
        self.fps = fps
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption('Rocket League')
        
        # Game state
        self.running = True
        self.paused = False
        self.time_elapsed = 0.0
        self.match_duration = 300.0  # 5 minutes
        
        # Arena configuration
        self.arena_bounds = {
            'width': 100,
            'length': 100,
            'height': 200
        }
        
        # Goal areas
        self.goal_blue = {
            'x_min': -20,
            'x_max': 20,
            'z_min': -110,
            'z_max': -95,
            'y_max': 30
        }
        self.goal_orange = {
            'x_min': -20,
            'x_max': 20,
            'z_min': 95,
            'z_max': 110,
            'y_max': 30
        }
        
        # Game objects
        self.ball = Ball(Vector3(0, 50, 0))
        self.players: List[Player] = [
            Player(team=0, pos=Vector3(-50, 10, -50)),
            Player(team=0, pos=Vector3(0, 10, -50)),
            Player(team=0, pos=Vector3(50, 10, -50)),
            Player(team=1, pos=Vector3(-50, 10, 50)),
            Player(team=1, pos=Vector3(0, 10, 50)),
            Player(team=1, pos=Vector3(50, 10, 50)),
        ]
        
        # Scoring
        self.scoring = ScoringSystem()
        for i, player in enumerate(self.players):
            self.scoring.add_player(i, player.team)
        
        # Replay recording
        self.replay_recorder = ReplayRecorder()
        self.recording = True
        
        # Controls
        self.controls = {
            pygame.K_w: 'forward',
            pygame.K_a: 'left',
            pygame.K_s: 'backward',
            pygame.K_d: 'right',
            pygame.K_SPACE: 'jump',
            pygame.K_e: 'boost',
            pygame.K_r: 'reset'
        }
        self.player_controls = {i: {k: False for k in ['forward', 'left', 'backward', 'right', 'jump', 'boost', 'reset']} for i in range(len(self.players))}
        
        # Active player (for keyboard control)
        self.active_player = 0
    
    def handle_input(self) -> None:
        """Handle user input"""
        keys = pygame.key.get_pressed()
        
        # Update controls for active player
        controls = self.player_controls[self.active_player]
        controls['forward'] = keys[pygame.K_w]
        controls['left'] = keys[pygame.K_a]
        controls['backward'] = keys[pygame.K_s]
        controls['right'] = keys[pygame.K_d]
        controls['jump'] = keys[pygame.K_SPACE]
        controls['boost'] = keys[pygame.K_e]
        controls['reset'] = keys[pygame.K_r]
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.paused = not self.paused
                elif event.key == pygame.K_q:
                    self.running = False
                elif event.key == pygame.K_TAB:
                    # Switch active player
                    self.active_player = (self.active_player + 1) % len(self.players)
                elif event.key == pygame.K_r:
                    self.reset_game()
    
    def update(self, dt: float) -> None:
        """Update game state"""
        if self.paused:
            return
        
        self.time_elapsed += dt
        
        # Update players
        for i, player in enumerate(self.players):
            player.update(dt, self.player_controls[i], self.arena_bounds)
        
        # Update ball
        self.ball.update(dt, self.arena_bounds)
        
        # Check player-ball collisions
        for i, player in enumerate(self.players):
            if player.check_ball_collision(self.ball):
                self.scoring.record_hit(i)
        
        # Check for goals
        if self.ball.check_goal(self.goal_blue):
            # Orange scores
            self.scoring.add_goal(1, self.active_player, self.time_elapsed, self.ball.position.to_tuple())
            self.reset_ball()
        elif self.ball.check_goal(self.goal_orange):
            # Blue scores
            self.scoring.add_goal(0, self.active_player, self.time_elapsed, self.ball.position.to_tuple())
            self.reset_ball()
        
        # Record replay
        if self.recording:
            self.replay_recorder.record_frame(
                self.ball,
                self.players,
                self.scoring.team_scores
            )
        
        # Check if match is over
        if self.time_elapsed >= self.match_duration:
            self.end_match()
    
    def reset_ball(self) -> None:
        """Reset ball to center"""
        self.ball.reset()
    
    def reset_game(self) -> None:
        """Reset entire game"""
        self.ball.reset()
        for player in self.players:
            player.reset()
        self.time_elapsed = 0.0
        self.scoring = ScoringSystem()
        for i, player in enumerate(self.players):
            self.scoring.add_player(i, player.team)
        self.replay_recorder = ReplayRecorder()
    
    def end_match(self) -> None:
        """End the match and save replay"""
        self.running = False
        replay_path = self.replay_recorder.save_replay()
        print(f"Match ended. Replay saved to {replay_path}")
        
        # Print summary
        summary = self.scoring.get_game_summary()
        print(f"\nFinal Score: Blue {summary['blue_score']} - {summary['orange_score']} Orange")
    
    def draw(self) -> None:
        """Render game to screen"""
        self.screen.fill((10, 10, 20))  # Dark background
        
        # Draw arena
        self._draw_arena()
        
        # Project 3D to 2D and draw game objects
        self._draw_ball()
        self._draw_players()
        
        # Draw UI
        self._draw_ui()
        
        pygame.display.flip()
    
    def _project_3d_to_2d(self, pos: Vector3) -> Tuple[int, int]:
        """Simple orthographic projection from 3D to 2D"""
        # Scale and center coordinates
        scale = 3
        center_x = self.width // 2
        center_y = self.height // 2
        
        # Project: use x and z for 2D view
        screen_x = int(center_x + pos.x * scale)
        screen_y = int(center_y + pos.z * scale)
        
        # Add height as color intensity
        height_factor = max(0, min(1, pos.y / 200))
        
        return (screen_x, screen_y), height_factor
    
    def _draw_arena(self) -> None:
        """Draw arena bounds"""
        scale = 3
        center_x = self.width // 2
        center_y = self.height // 2
        
        arena_w = int(self.arena_bounds['width'] * scale)
        arena_l = int(self.arena_bounds['length'] * scale)
        
        # Draw field
        field_color = (20, 80, 20)
        pygame.draw.rect(self.screen, field_color,
                         (center_x - arena_w, center_y - arena_l, arena_w*2, arena_l*2))
        
        # Draw goals
        goal_w = int(20 * scale)
        goal_l = int(15 * scale)
        goal_color_blue = (50, 100, 200)
        goal_color_orange = (255, 150, 50)
        
        # Blue goal
        pygame.draw.rect(self.screen, goal_color_blue,
                         (center_x - goal_w, center_y - arena_l - goal_l, goal_w*2, goal_l))
        
        # Orange goal
        pygame.draw.rect(self.screen, goal_color_orange,
                         (center_x - goal_w, center_y + arena_l, goal_w*2, goal_l))
        
        # Draw center line
        pygame.draw.line(self.screen, (100, 100, 100),
                         (center_x - arena_w, center_y),
                         (center_x + arena_w, center_y), 2)
    
    def _draw_ball(self) -> None:
        """Draw the ball"""
        pos_2d, height_factor = self._project_3d_to_2d(self.ball.position)
        
        # Color ball based on height
        color = (255, 200 + int(55 * height_factor), 100)
        pygame.draw.circle(self.screen, color, pos_2d, int(5 + height_factor * 5))
    
    def _draw_players(self) -> None:
        """Draw all players"""
        for player in self.players:
            pos_2d, height_factor = self._project_3d_to_2d(player.position)
            
            # Draw player circle
            pygame.draw.circle(self.screen, player.color, pos_2d, 8)
            
            # Draw jump indicator
            if player.is_jumping:
                pygame.draw.circle(self.screen, (255, 255, 0), pos_2d, 10, 2)
    
    def _draw_ui(self) -> None:
        """Draw UI elements"""
        font_large = pygame.font.Font(None, 48)
        font_small = pygame.font.Font(None, 24)
        
        # Score
        blue_score = self.scoring.get_team_score(0)
        orange_score = self.scoring.get_team_score(1)
        score_text = f"{blue_score} - {orange_score}"
        score_surface = font_large.render(score_text, True, (200, 200, 200))
        self.screen.blit(score_surface, (self.width // 2 - 50, 20))
        
        # Time
        minutes = int(self.time_elapsed) // 60
        seconds = int(self.time_elapsed) % 60
        time_text = f"{minutes}:{seconds:02d}"
        time_surface = font_small.render(time_text, True, (200, 200, 200))
        self.screen.blit(time_surface, (20, 20))
        
        # Active player boost
        active_player = self.players[self.active_player]
        boost_text = f"Boost: {active_player.boost_amount:.0f}%"
        boost_surface = font_small.render(boost_text, True, (200, 200, 200))
        self.screen.blit(boost_surface, (20, 50))
        
        # Paused indicator
        if self.paused:
            pause_surface = font_large.render("PAUSED", True, (255, 100, 100))
            self.screen.blit(pause_surface, (self.width // 2 - 100, self.height // 2))
        
        # Controls info
        controls_text = "WASD:Move Space:Jump E:Boost R:Reset TAB:Switch ESC:Pause Q:Quit"
        controls_surface = font_small.render(controls_text, True, (150, 150, 150))
        self.screen.blit(controls_surface, (20, self.height - 30))
    
    def run(self) -> None:
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(self.fps) / 1000.0  # Delta time in seconds
            
            self.handle_input()
            self.update(dt)
            self.draw()
        
        # Save replay on exit
        if self.recording:
            replay_path = self.replay_recorder.save_replay()
            print(f"Replay saved to {replay_path}")
        
        pygame.quit()
