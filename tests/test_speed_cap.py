import pytest
from ai.game_modes import GameMode
from typing import List, Any

class MockBall:
    def __init__(self, ball_id: int):
        self.id = ball_id
        self.alive = True
        self.ball_type = "player"
        self.team = "A"
        self.speed = 400.0
        self.base_speed = 400.0

class MockWorld:
    def __init__(self):
        self.match_time = 0.0
        self.dead_balls = []

def test_speed_cap_reduces_speed():
    # Setup
    world = MockWorld()
    balls = [MockBall(1), MockBall(2)]

    game_mode = GameMode()
    game_mode.setup(world, balls)

    # Tick for 100 seconds (delta = 100.0 for faster testing)
    game_mode.tick(world, balls, delta=100.0)

    # speed_cap should be max(30.0, 300.0 - (100.0 * 1.5)) = max(30.0, 150.0) = 150.0
    # Expected speed and base_speed is 150.0 for balls initially at 400.0
    for b in balls:
        assert b.speed == 150.0
        assert b.base_speed == 150.0

def test_speed_cap_minimum_cap():
    # Setup
    world = MockWorld()
    balls = [MockBall(1)]

    game_mode = GameMode()
    game_mode.setup(world, balls)

    # Tick for 1000 seconds
    game_mode.tick(world, balls, delta=1000.0)

    # speed_cap should be max(30.0, 300.0 - (1000.0 * 1.5)) = max(30.0, -1200.0) = 30.0
    for b in balls:
        assert b.speed == 30.0
        assert b.base_speed == 30.0

def test_speed_cap_spectators_unaffected():
    # Setup
    world = MockWorld()
    spectator = MockBall(1)
    spectator.ball_type = "spectator"
    balls = [spectator]

    game_mode = GameMode()
    game_mode.setup(world, balls)

    game_mode.tick(world, balls, delta=100.0)

    assert spectator.speed == 400.0
    assert spectator.base_speed == 400.0

if __name__ == '__main__':
    pass
