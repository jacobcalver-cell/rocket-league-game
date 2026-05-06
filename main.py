#!/usr/bin/env python3
"""
Rocket League Game - Main Entry Point

A Python-based Rocket League game with:
- Ball physics simulation
- Player movement controls
- Scoring system
- Replay analyzer
"""

import pygame
import sys
from game import RocketLeagueGame

def main():
    """Initialize and run the game"""
    # Initialize Pygame
    pygame.init()
    
    try:
        # Create and run game
        game = RocketLeagueGame(width=1600, height=900, fps=60)
        game.run()
    except Exception as e:
        print(f"Error running game: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()
