import pytest
import sys
import os
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.action import Action

class MockBall:
    def __init__(self, id="p1", x=0, y=0, team="red"):
        self.id = id
        self.x = x
        self.y = y
        self.radius = 10.0
        self.alive = True
        self.team = team

class MockBooster:
    def __init__(self, x=0, y=0, kind="echo_booster"):
        self.x = x
        self.y = y
        self.radius = 10.0
        self.kind = kind
        self.active = True

class MockArena:
    def __init__(self, hazards=None):
        self.hazards = hazards or []

class MockWorld:
    def __init__(self, boosters=None, arena=None, balls=None, next_id=1):
        self.boosters = boosters or []
        self.arena = arena or MockArena()
        self.balls = balls or []
        self.next_id = next_id

def test_echo_spawning_and_slowing():
    ball = MockBall(x=10, y=10)
    ball.echo_booster_timer = 5.0
    ball.echo_booster_spawn_timer = 0.0
    ball.vx = 50.0
    ball.vy = 0.0

    enemy = MockBall(id="p2", x=10, y=10, team="blue")

    world = MockWorld(balls=[ball, enemy])
    action = Action(ball, world)

    # 1. Action execute should spawn echo
    action.execute("idle", 0.1)

    # Assert echo spawned
    assert len(world.arena.hazards) > 0
    echo = world.arena.hazards[-1]
    assert echo.kind == "echo_trail"
    assert echo.x == 10
    assert echo.y == 10
    assert getattr(ball, "echo_booster_spawn_timer", 0.0) > 0.0

    # 2. Let's make sure the echo slows the enemy
    enemy_action = Action(enemy, world)
    enemy.speed_multiplier = 1.0
    enemy.x = echo.x
    enemy.y = echo.y
    enemy_action.execute("idle", 0.1)

    assert getattr(enemy, "slow_timer", 0.0) > 0.0
    # The echo might be consumed, let's see

if __name__ == "__main__":
    pytest.main([__file__])
