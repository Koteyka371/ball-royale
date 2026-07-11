import sys
import os

# Ensure src/ is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai.action import Action
from arena.arena_types import AutumnArena

class MockBall:
    def __init__(self):
        self.id = 1
        self.x = 500.0
        self.y = 500.0
        self.vx = 10.0
        self.vy = 0.0
        self.radius = 15.0
        self.skill = "wind_rider"
        self.skill_timer = 0.0
        self.speed_buff_timer = 0.0

    def use_skill(self):
        pass

class MockWorld:
    def __init__(self, arena):
        self.arena = arena
        self.events = []
        self.balls = []

def test_wind_rider_skill_windy():
    arena = AutumnArena()
    # verify arena is windy
    assert getattr(arena, "is_windy", False) == True

    ball = MockBall()
    world = MockWorld(arena)
    action = Action(ball, world)

    # execute use_skill
    action._use_skill()

    assert ball.speed_buff_timer == 5.0
    # check that we moved and x increased since vx is positive and vy is 0
    assert ball.x > 500.0
    assert ball.y == 500.0

    # Check events
    assert len(world.events) > 0
    assert any(e["type"] == "skill_used" and e["data"]["skill"] == "wind_rider" for e in world.events)

def test_wind_rider_skill_not_windy():
    class NormalArena:
        is_windy = False
        width = 1000
        height = 1000
        def clamp_position(self, x, y, r):
            return (x, y, False)

    arena = NormalArena()
    ball = MockBall()
    world = MockWorld(arena)
    action = Action(ball, world)

    action._use_skill()

    assert ball.speed_buff_timer == 0.0
    assert ball.x == 500.0
    assert ball.y == 500.0
    assert len(world.events) == 0

if __name__ == "__main__":
    test_wind_rider_skill_windy()
    test_wind_rider_skill_not_windy()
    print("All tests passed")
