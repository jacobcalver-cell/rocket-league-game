# Rocket League Game

A Python-based Rocket League game implementation with realistic ball physics, player movement controls, scoring system, and replay analyzer.

## Features

- **Ball Physics Simulation**: Realistic ball movement with gravity, velocity, and collision detection
- **Player Movement Controls**: WASD for movement, Space for jump, E for boost, R for reset
- **Scoring System**: Track goals and maintain match statistics
- **Replay Analyzer**: Record and analyze game replays
- **Custom Game Modes**: Practice, Training, and Custom Match modes

## Requirements

- Python 3.8+
- pygame
- numpy

## Installation

```bash
pip install -r requirements.txt
```

## Running the Game

```bash
python main.py
```

## Controls

- **W/A/S/D**: Move player
- **Space**: Jump
- **E**: Boost
- **R**: Reset position
- **ESC**: Pause/Menu
- **Q**: Quit game

## Game Modes

1. **Practice Mode**: Train against AI
2. **Training Mode**: Work on specific skills
3. **Custom Match**: Play with custom settings
4. **Replay Mode**: Analyze previous matches

## Architecture

- `main.py`: Game entry point
- `physics.py`: Ball physics engine
- `player.py`: Player class and controls
- `game.py`: Main game loop and logic
- `scoring.py`: Scoring system
- `replay.py`: Replay recording and analysis
- `ui.py`: User interface components

## License

MIT License
