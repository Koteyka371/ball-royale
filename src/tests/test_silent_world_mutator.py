import pytest
import sys
sys.path.append("src")
from ai.game_modes import GAME_MODES
from ai.action import Action

class MockWorld:
    def __init__(self):
        self.balls = []
        self.arena = MockArena()
        self.events = []
        self.mutators_active = True
        self.mutators = ["silent_world"]

class MockArena:
    def __init__(self):
        self.hazards = []
    def clamp_position(self, x, y, radius):
        return x, y, False
    def update_zone(self, tick, delta):
        pass

class MockBall:
    def __init__(self, x=0, y=0, ball_type="player", alive=True):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.radius = 25
        self.alive = alive
        self.ball_type = ball_type
        self.hologram_clones = []
        self.silence_timer = 0.0
        self.silencer_timer = 0.0

class MockHazard:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.active = True
        self.duration = 10.0
        self.radius = 100.0
        self.damage = 10.0
        self.owner_id = "test"
        self.owner = None

def test_silent_world_mutator_tick():
    world = MockWorld()
    b1 = MockBall()
    world.balls = [b1]

    mutator = GAME_MODES["silent_world_mutator"]
    mutator.setup(world, [b1])
    mutator.tick(world, [b1], 0.1)

    # Should apply silence and silencer timers
    assert b1.silence_timer >= 2.0
    assert b1.silencer_timer >= 2.0

def test_silent_world_mutator_sound_mine():
    world = MockWorld()
    b1 = MockBall(x=10, y=10)
    world.balls = [b1]

    hazard = MockHazard(10, 10, "sound_mine")
    world.arena.hazards.append(hazard)

    # Action evaluating a loud skill
    action = Action(b1, world)
    action.ball.active_skill_name = "dash"
    action.execute("dash", 0.1)

    # Normally dash would trigger the sound_mine (set duration to 0), but it shouldn't because of mutator
    assert hazard.duration == 10.0
