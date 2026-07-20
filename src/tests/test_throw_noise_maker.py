import pytest
import sys
import math
sys.path.append('src')
from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.balls = []
        self.next_id = 20000

class MockBall:
    def __init__(self, id, x, y, team):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.radius = 10.0
        self.hp = 100
        self.max_hp = 100
        self.alive = True
        self.skill_timer = 0.0
        self.skill = "throw_noise_maker"
        self.active_skill = "throw_noise_maker"
        self.stutter_timer = 0.0
        self.taunt_timer = 0.0
        self.is_confused = False

def test_throw_noise_maker_creates_hazard():
    world = MockWorld()
    ball = MockBall(1, 100, 100, "A")
    enemy = MockBall(2, 200, 100, "B")
    world.balls = [ball, enemy]

    action = Action(ball, world)
    # mock get enemies
    action._get_enemies = lambda: [enemy]

    action._use_skill()

    # hazard should be created
    assert len(world.arena.hazards) == 1
    hazard = world.arena.hazards[0]
    assert getattr(hazard, "kind", "") == "thrown_noise_maker"
    assert hazard.owner_id == 1
    assert hazard.vx > 0  # Should be thrown towards (200, 100)
    assert hazard.duration == 2.0

def test_thrown_noise_maker_hazard_expiration():
    world = MockWorld()
    ball = MockBall(1, 100, 100, "A")
    world.balls = [ball]

    action = Action(ball, world)

    class Hazard:
        def __init__(self):
            self.kind = "thrown_noise_maker"
            self.duration = 0.1
            self.x = 300
            self.y = 300
            self.owner_id = 1

    hazard = Hazard()
    world.arena.hazards.append(hazard)

    action.execute(strategy='offensive', delta=0.2)

    # hazard should be removed
    assert hazard not in world.arena.hazards

    # events should be added
    assert any(e['type'] == 'fake_footstep' and e['data']['x'] == 300 for e in world.events)
    assert any(e['type'] == 'visual_effect' and e['data']['type'] == 'visual_noise' for e in world.events)

    # 3 decoys should be added
    decoys = [b for b in world.balls if getattr(b, "is_decoy", False)]
    assert len(decoys) == 3
    for decoy in decoys:
        assert decoy.is_illusion is True
        assert decoy.hp == 1.0
        assert decoy.decoy_type == "noise_phantom"
        # velocities should not be zero
        assert decoy.vx != 0 or decoy.vy != 0
