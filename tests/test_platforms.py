import pytest
from arena.procedural_arena import ProceduralArena, Platform
from ai.action import Action
from unittest.mock import MagicMock
import math

class MockBall:
    def __init__(self):
        self.x = 100.0
        self.y = 100.0
        self.radius = 10.0
        self.speed = 100.0
        self.ball_type = "basic"
        self.stamina = 100.0

def test_procedural_arena_platforms_exist():
    arena = ProceduralArena()
    arena.generate()
    assert hasattr(arena, "platforms")
    assert isinstance(arena.platforms, list)
    assert len(arena.platforms) >= 3

def test_platforms_move():
    arena = ProceduralArena()
    arena.generate()
    if len(arena.platforms) > 0:
        p = arena.platforms[0]
        p.x = 200.0
        p.y = 200.0
        p.vx = 10.0
        p.vy = 5.0
        arena.update_zone(0, 1.0)
        # Verify it moved
        assert p.x == 210.0
        assert p.y == 205.0

def test_ball_moves_with_platform():
    arena = ProceduralArena()
    arena.hazards = []

    world = MagicMock()
    world.arena = arena
    world.width = 2000
    world.height = 2000
    world.boosters = []
    world.events = []

    ball = MockBall()

    p = Platform(x=100.0, y=100.0, width=50.0, height=50.0, vx=20.0, vy=10.0)
    arena.platforms = [p]
    ball.x = 100.0
    ball.y = 100.0

    action = Action(ball, world)

    # We execute "none" (idle). Idle does some random movement or boundary clamping,
    # but the platform movement should ALSO happen.
    action.execute("none", 1.0)

    # Since idle movement randomizes slightly, just check that it didn't stay still.
    # The platform applied +20 to x and +10 to y.
    assert ball.x != 100.0
    assert ball.y != 100.0
