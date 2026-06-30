import sys
import os
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from ai.action import Action

class MockHazard:
    def __init__(self, x, y, kind="spikes", damage=20.0, radius=20.0):
        self.x = x
        self.y = y
        self.kind = kind
        self.damage = damage
        self.radius = radius

class MockArena:
    def __init__(self, hazards=None):
        self.hazards = hazards if hazards is not None else []

class MockWorld:
    def __init__(self, arena=None):
        self.arena = arena if arena is not None else MockArena()
        self.balls = []

class MockBall:
    def __init__(self, x=0, y=0, skill="convert_hazard"):
        self.x = x
        self.y = y
        self.skill = skill
        self.active_skill = skill
        self.radius = 10.0
        self.emitted_particles = []

def test_convert_hazard():
    ball = MockBall(x=0, y=0, skill="convert_hazard")
    hazard_spikes = MockHazard(x=50, y=0, kind="spikes", damage=20.0, radius=20.0)
    hazard_lava = MockHazard(x=100, y=0, kind="lava", damage=40.0, radius=20.0)
    hazard_far = MockHazard(x=300, y=0, kind="spikes", damage=20.0, radius=20.0)
    hazard_safe = MockHazard(x=50, y=50, kind="healing_spring", damage=0.0, radius=20.0)

    arena = MockArena(hazards=[hazard_spikes, hazard_lava, hazard_far, hazard_safe])
    world = MockWorld(arena=arena)

    action = Action(ball, world)
    action.execute("use skill", 0.1)

    assert hazard_spikes.kind == "healing_spring"
    assert hazard_spikes.damage == 0.0
    assert hasattr(hazard_spikes, "duration") and hazard_spikes.duration == 5.0

    assert hazard_lava.kind == "healing_spring"
    assert hazard_lava.damage == 0.0
    assert hasattr(hazard_lava, "duration") and hazard_lava.duration == 5.0

    assert hazard_far.kind == "spikes"
    assert hazard_far.damage == 20.0
    assert not hasattr(hazard_far, "duration")

    assert hazard_safe.kind == "healing_spring"

    particle_emitted = any(p.get("skill") == "convert_hazard" for p in ball.emitted_particles)
    assert particle_emitted

if __name__ == "__main__":
    test_convert_hazard()
    print("test_convert_hazard passed!")
