import pytest
from ai.action import Action
from arena.procedural_arena import Hazard

class MockArena:
    def __init__(self, w, h):
        self.width = w
        self.height = h
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena(800, 600)
        self.balls = []

class MockBall:
    def __init__(self, bid, btype):
        self.id = bid
        self.ball_type = btype
        self.x = 400.0
        self.y = 100.0
        self.radius = 10.0
        self.speed = 100.0
        self.web_drop_timer = 0.0
        self.alive = True
        self.current_action = "idle"

def test_spider_wall_crawl_stick_top():
    ball = MockBall(1, "spider")
    ball.x = 400.0
    ball.y = 50.0  # Closer to top wall (y=0)
    world = MockWorld()

    action = Action(ball, world)
    action.execute("wall_crawl", 0.1)

    # Should snap to top wall (radius = 10)
    assert ball.y == 10.0
    # Should move right (x increases)
    assert ball.x > 400.0
    assert ball.current_action == "wall_crawl"

def test_spider_wall_crawl_web_drop():
    ball = MockBall(1, "spider")
    ball.web_drop_timer = 0.05
    world = MockWorld()

    action = Action(ball, world)
    action.execute("wall_crawl", 0.1)  # Timer goes to -0.05 -> drops web -> resets to 5.0

    assert ball.web_drop_timer == 5.0
    assert len(world.arena.hazards) == 1
    hazard = world.arena.hazards[0]
    assert hazard.kind == "spider_web"
    assert getattr(hazard, "owner_id", None) == 1
