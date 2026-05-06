import pygame
from physics import Vector3, Ball
from typing import Dict, Tuple

class Player:
    """Player class with controls and physics"""
    def __init__(self, team: int, pos: Vector3 = None):
        self.team = team  # 0 = blue, 1 = orange
        self.position = pos or Vector3(-50 if team == 0 else 50, 10, 0)
        self.velocity = Vector3(0, 0, 0)
        self.acceleration = Vector3(0, 0, 0)
        self.radius = 2.0
        self.mass = 1.0  # kg
        self.max_speed = 30.0  # m/s
        self.acceleration_rate = 50.0  # m/s^2
        self.boost_force = 100.0  # additional acceleration
        self.jump_force = 50.0  # jump velocity
        self.gravity = -9.81
        self.is_jumping = False
        self.boost_amount = 100.0  # boost fuel
        self.max_boost = 100.0
        self.boost_recharge_rate = 10.0  # per second
        self.color = (0, 0, 255) if team == 0 else (255, 165, 0)
        self.goals = 0
        self.aerial_time = 0.0
    
    def update(self, dt: float, controls: Dict[str, bool], arena_bounds: dict) -> None:
        """Update player physics and movement"""
        # Reset acceleration
        self.acceleration = Vector3(0, 0, 0)
        
        # Handle movement controls
        if controls['forward']:
            self.acceleration.z += self.acceleration_rate
        if controls['backward']:
            self.acceleration.z -= self.acceleration_rate
        if controls['left']:
            self.acceleration.x -= self.acceleration_rate
        if controls['right']:
            self.acceleration.x += self.acceleration_rate
        
        # Handle boost
        if controls['boost'] and self.boost_amount > 0:
            boost_direction = Vector3(self.acceleration.x, 0, self.acceleration.z).normalize()
            self.acceleration = self.acceleration + boost_direction * self.boost_force
            self.boost_amount -= 50.0 * dt  # consume boost
        else:
            # Recharge boost
            self.boost_amount = min(self.max_boost, self.boost_amount + self.boost_recharge_rate * dt)
        
        # Handle jump
        if controls['jump'] and not self.is_jumping:
            self.velocity.y = self.jump_force
            self.is_jumping = True
        
        # Apply gravity
        self.acceleration.y = self.gravity
        
        # Update velocity
        self.velocity = self.velocity + self.acceleration * dt
        
        # Limit horizontal speed
        horizontal_speed = (self.velocity.x**2 + self.velocity.z**2)**0.5
        if horizontal_speed > self.max_speed:
            scale = self.max_speed / horizontal_speed
            self.velocity.x *= scale
            self.velocity.z *= scale
        
        # Update position
        self.position = self.position + self.velocity * dt
        
        # Handle ground collision
        if self.position.y - self.radius <= 0:
            self.position.y = self.radius
            self.velocity.y = 0
            self.is_jumping = False
        
        # Handle arena boundaries
        self._handle_boundaries(arena_bounds)
        
        # Update aerial time
        if self.position.y > self.radius:
            self.aerial_time += dt
        else:
            self.aerial_time = 0
    
    def _handle_boundaries(self, arena_bounds: dict) -> None:
        """Keep player within arena bounds"""
        max_width = arena_bounds.get('width', 100)
        max_length = arena_bounds.get('length', 100)
        max_height = arena_bounds.get('height', 200)
        
        # Clamp position within bounds
        self.position.x = max(-max_width, min(max_width, self.position.x))
        self.position.z = max(-max_length, min(max_length, self.position.z))
        self.position.y = max(self.radius, min(max_height - self.radius, self.position.y))
    
    def jump(self) -> None:
        """Make player jump"""
        if not self.is_jumping:
            self.velocity.y = self.jump_force
            self.is_jumping = True
    
    def apply_force(self, force: Vector3) -> None:
        """Apply a force to the player"""
        acceleration = force / self.mass
        self.velocity = self.velocity + acceleration
    
    def check_ball_collision(self, ball: Ball) -> bool:
        """Check and handle collision with ball"""
        distance = (self.position - ball.position).magnitude()
        collision_distance = self.radius + ball.radius
        
        if distance < collision_distance:
            # Calculate collision response
            collision_normal = (ball.position - self.position).normalize()
            relative_velocity = ball.velocity - self.velocity
            velocity_along_normal = relative_velocity.dot(collision_normal)
            
            # Only collide if ball is moving towards player
            if velocity_along_normal < 0:
                # Apply impulse
                impulse = collision_normal * velocity_along_normal * -1.2
                ball.apply_force(impulse)
                return True
        
        return False
    
    def reset(self) -> None:
        """Reset player to starting position"""
        self.position = Vector3(-50 if self.team == 0 else 50, 10, 0)
        self.velocity = Vector3(0, 0, 0)
        self.acceleration = Vector3(0, 0, 0)
        self.is_jumping = False
        self.boost_amount = self.max_boost
