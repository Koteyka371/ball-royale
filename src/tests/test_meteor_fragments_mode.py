import math
import random
from ai.game_modes import MeteorFragmentsMode
from arena.arena_types import ProceduralArena

class MockBall:
    def __init__(self, id, team, ball_type):
        self.id = id
        self.team = team
        self.ball_type = ball_type
        self.x = 100.0
        self.y = 100.0
        self.radius = 15.0
        self.damage_boost_timer = 0.0

class MockWorld:
    def __init__(self):
        self.arena = ProceduralArena(2000.0)

def test_meteor_fragments_mode():
    mode = MeteorFragmentsMode()
    world = MockWorld()
    ball = MockBall(1, "team1", "player")

    # Fast forward meteor spawn
    mode.meteor_timer = 0.01
    mode.tick(world, [ball], delta=0.016)

    assert any(h.kind == "meteor_falling" for h in world.arena.hazards)

    # Fast forward meteor explosion
    meteor = next(h for h in world.arena.hazards if h.kind == "meteor_falling")
    meteor.timer = 0.01
    meteor.x = 100.0
    meteor.y = 100.0

    mode.tick(world, [ball], delta=0.016)

    assert not any(h.kind == "meteor_falling" for h in world.arena.hazards)
    assert any(h.kind == "glowing_fragment" for h in world.arena.hazards)

    # Absorb fragment
    fragment = next(h for h in world.arena.hazards if h.kind == "glowing_fragment")
    assert fragment.x == 100.0
    assert fragment.y == 100.0

    mode.tick(world, [ball], delta=0.016)

    assert ball.damage_boost_timer > 0.0
    assert not any(h.kind == "glowing_fragment" for h in world.arena.hazards)

if __name__ == '__main__':
    test_meteor_fragments_mode()
    print("Test passed.")
