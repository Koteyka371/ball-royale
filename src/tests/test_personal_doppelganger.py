import pytest
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, id_val, ball_type="basic", alive=True):
        self.id = id_val
        self.ball_type = ball_type
        self.alive = alive
        self.x = 100.0
        self.y = 100.0
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 20.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.team = "red"
        self.speed = 100.0
        self.base_speed = 100.0
        self.damage = 25.0
        self.base_damage = 25.0
        self.skills = ["dash"]
        self.inventory = []
        self.active_skill = None
        self.skill_timer = 0.0
        self._prev_active_skill = None

class MockWorld:
    def __init__(self):
        self.balls = []

def test_personal_doppelganger_spawn():
    mode = GAME_MODES.get("personal_doppelganger")
    assert mode is not None

    world = MockWorld()
    b1 = MockBall(1)
    b2 = MockBall(2, ball_type="spectator")
    world.balls = [b1, b2]

    mode.setup(world, world.balls)

    assert len(world.balls) == 3
    assert b1.id in mode.doppelgangers
    assert b2.id not in mode.doppelgangers

    dop_id = mode.doppelgangers[b1.id]
    dop = next((b for b in world.balls if b.id == dop_id), None)

    assert dop is not None
    assert getattr(dop, "is_personal_doppelganger", False)
    assert dop.owner_id == b1.id
    assert dop.ball_type == b1.ball_type
    assert dop.team == b1.team
    assert dop.skills == b1.skills

def test_personal_doppelganger_takeover():
    mode = GAME_MODES.get("personal_doppelganger")

    world = MockWorld()
    b1 = MockBall(1)
    world.balls = [b1]

    mode.setup(world, world.balls)
    dop = next(b for b in world.balls if getattr(b, "is_personal_doppelganger", False))

    # Simulate movement
    dop.x = 500.0
    dop.y = 500.0
    dop.hp = 75.0

    # Player dies
    b1.alive = False

    mode.tick(world, world.balls, 0.016)

    assert b1.alive is True
    assert dop.alive is False
    assert b1.x == 500.0
    assert b1.y == 500.0
    assert b1.hp == 75.0

def test_personal_doppelganger_mimic_attack():
    mode = GAME_MODES.get("personal_doppelganger")

    world = MockWorld()
    b1 = MockBall(1)
    world.balls = [b1]

    mode.setup(world, world.balls)
    dop = next(b for b in world.balls if getattr(b, "is_personal_doppelganger", False))

    b1.active_skill = "dash"
    b1.skill_timer = 2.0

    mode.tick(world, world.balls, 0.016)

    assert dop.active_skill == "dash"
    assert dop.skill_timer == 2.0
