import numpy as np
from typing import Tuple, List

class Vector3:
    """3D Vector class for game physics"""
    def __init__(self, x: float = 0, y: float = 0, z: float = 0):
        self.x = x
        self.y = y
        self.z = z
    
    def __add__(self, other: 'Vector3') -> 'Vector3':
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other: 'Vector3') -> 'Vector3':
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar: float) -> 'Vector3':
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def __truediv__(self, scalar: float) -> 'Vector3':
        return Vector3(self.x / scalar, self.y / scalar, self.z / scalar)
    
    def magnitude(self) -> float:
        return np.sqrt(self.x**2 + self.y**2 + self.z**2)
    
    def normalize(self) -> 'Vector3':
        mag = self.magnitude()
        if mag == 0:
            return Vector3(0, 0, 0)
        return self / mag
    
    def dot(self, other: 'Vector3') -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def to_tuple(self) -> Tuple[float, float, float]:
        return (self.x, self.y, self.z)


class Ball:
    """Ball physics simulation"""
    def __init__(self, pos: Vector3 = None, radius: float = 1.0):
        self.position = pos or Vector3(0, 50, 0)
        self.velocity = Vector3(0, 0, 0)
        self.acceleration = Vector3(0, 0, 0)
        self.radius = radius
        self.mass = 0.5  # kg
        self.gravity = Vector3(0, -9.81, 0)  # m/s^2
        self.friction = 0.98  # friction coefficient
        self.bounce_coefficient = 0.75  # bounce factor
    
    def update(self, dt: float, arena_bounds: dict) -> None:
        """Update ball physics"""
        # Apply gravity
        self.acceleration = self.gravity.copy() if hasattr(self.gravity, 'copy') else Vector3(self.gravity.x, self.gravity.y, self.gravity.z)
        
        # Update velocity
        self.velocity = self.velocity + self.acceleration * dt
        
        # Apply friction
        self.velocity = self.velocity * self.friction
        
        # Update position
        self.position = self.position + self.velocity * dt
        
        # Boundary collision
        self._handle_collisions(arena_bounds)
    
    def _handle_collisions(self, arena_bounds: dict) -> None:
        """Handle ball collisions with arena walls and ground"""
        # Ground collision
        if self.position.y - self.radius <= 0:
            self.position.y = self.radius
            self.velocity.y = abs(self.velocity.y) * self.bounce_coefficient
        
        # Ceiling collision
        max_height = arena_bounds.get('height', 200)
        if self.position.y + self.radius >= max_height:
            self.position.y = max_height - self.radius
            self.velocity.y = -abs(self.velocity.y) * self.bounce_coefficient
        
        # Side walls
        max_width = arena_bounds.get('width', 200)
        if self.position.x - self.radius <= -max_width:
            self.position.x = -max_width + self.radius
            self.velocity.x = abs(self.velocity.x) * self.bounce_coefficient
        if self.position.x + self.radius >= max_width:
            self.position.x = max_width - self.radius
            self.velocity.x = -abs(self.velocity.x) * self.bounce_coefficient
        
        # End walls
        max_length = arena_bounds.get('length', 200)
        if self.position.z - self.radius <= -max_length:
            self.position.z = -max_length + self.radius
            self.velocity.z = abs(self.velocity.z) * self.bounce_coefficient
        if self.position.z + self.radius >= max_length:
            self.position.z = max_length - self.radius
            self.velocity.z = -abs(self.velocity.z) * self.bounce_coefficient
    
    def apply_force(self, force: Vector3) -> None:
        """Apply a force to the ball"""
        acceleration = force / self.mass
        self.velocity = self.velocity + acceleration
    
    def check_collision_with_player(self, player_pos: Vector3, player_radius: float) -> bool:
        """Check if ball collides with player"""
        distance = (self.position - player_pos).magnitude()
        return distance < (self.radius + player_radius)
    
    def check_goal(self, goal_area: dict) -> bool:
        """Check if ball is in goal area"""
        return (goal_area['x_min'] <= self.position.x <= goal_area['x_max'] and
                goal_area['z_min'] <= self.position.z <= goal_area['z_max'] and
                self.position.y <= goal_area['y_max'])
    
    def reset(self) -> None:
        """Reset ball to center of arena"""
        self.position = Vector3(0, 50, 0)
        self.velocity = Vector3(0, 0, 0)
        self.acceleration = Vector3(0, 0, 0)
