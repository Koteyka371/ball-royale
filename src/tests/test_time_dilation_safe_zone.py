import pytest
from unittest.mock import MagicMock
from ai.game_modes import TimeDilationSafeZoneMode
from ai.action import Action

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.position = MagicMock()
        self.position.x = x
        self.position.y = y
        self.alive = True
        self.ball_type = "normal"
        self.base_speed = 100.0
        self.speed = 100.0
        self.skill_timer = 5.0
        self.hazard_immunity_timer = 0.0
        self.hp = 100.0
        self.damage = 20.0
        self.in_time_dilation_zone = False

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.dead_balls = []
        self.game_mode = None

    def add_event(self, kind, payload):
        pass

def test_time_dilation_safe_zone_mechanics():
    world = MockWorld()
    # Ball 1 inside the zone (centered at 500, 500, radius 500)
    ball_in = MockBall(1, 500.0, 500.0)
    # Ball 2 outside the zone
    ball_out = MockBall(2, 2000.0, 2000.0)

    world.balls = [ball_in, ball_out]

    mode = TimeDilationSafeZoneMode()
    mode.setup(world, world.balls)

    # Tick updates mode state and ball state
    mode.tick(world, world.balls, delta=0.1)

    # Verify ball inside zone
    assert ball_in.in_time_dilation_zone is True, "Ball inside zone should have the flag set"
    assert ball_in.speed == ball_in.base_speed * 0.5, "Ball inside zone should have half speed"
    assert ball_in.skill_timer > 5.0, "Ball inside zone should have its skill_timer increased (cooldown slowed)"
    assert ball_in.hazard_immunity_timer >= 0.1, "Ball inside zone should have hazard immunity"

    # Verify ball outside zone
    assert ball_out.in_time_dilation_zone is False, "Ball outside zone should not have the flag set"
    assert ball_out.speed == ball_out.base_speed, "Ball outside zone should retain normal speed"
    assert ball_out.skill_timer == 5.0, "Ball outside zone should not have its skill_timer affected by time dilation"

def test_time_dilation_damage_reduction():
    world = MockWorld()
    ball_in = MockBall(1, 500.0, 500.0)
    ball_in.in_time_dilation_zone = True

    attacker = MockBall(2, 600.0, 600.0)
    attacker.damage = 40.0

    action = Action(ball_in, world)
    action._attempt_damage_internal(attacker, ball_in)

    # original_damage of attacker should be halved to 20.0 during calculation
    assert attacker.damage == 20.0, "Attacker damage should be halved against a target in the time dilation zone"


def test_time_dilation_edge_cases():
    world = MockWorld()
    ball_in = MockBall(1, 500.0, 500.0)
    ball_in.skill_timer = 0.0 # should not increment

    world.balls = [ball_in]

    mode = TimeDilationSafeZoneMode()
    mode.setup(world, world.balls)

    mode.tick(world, world.balls, delta=0.1)

    assert ball_in.skill_timer == 0.0, "Skill timer should not increment if it is already 0"

    # Now move it outside
    ball_in.x = 2000.0
    ball_in.y = 2000.0
    ball_in.position.x = 2000.0
    ball_in.position.y = 2000.0
    mode.tick(world, world.balls, delta=0.1)

    assert ball_in.in_time_dilation_zone is False, "Ball should no longer be in zone"
    assert ball_in.speed == ball_in.base_speed, "Speed should be restored when exiting zone"
