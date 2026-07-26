import pytest
from unittest.mock import Mock
from ai.game_modes import RandomGravityShiftMode, GAME_MODES

def test_random_gravity_shift_mode_registered():
    assert 'random_gravity_shift' in GAME_MODES
    assert isinstance(GAME_MODES['random_gravity_shift'], RandomGravityShiftMode)

def test_random_gravity_shift_mode_tick():
    mode = RandomGravityShiftMode()
    world = Mock()
    world.add_event = Mock()
    world.arena = Mock()
    world.arena.hazards = []
    world.mutators = []
    world.boosters = []

    b = Mock()
    b.alive = True
    b.active = True
    b.ball_type = "normal"
    b.traits = []
    b.vx = 0.0
    b.vy = 0.0
    b.mass = 1.0

    balls = [b]

    # Fast forward to trigger a shift
    mode.shift_timer = 0.01

    mode.tick(world, balls, delta=0.016)

    assert world.add_event.called
    event_call = world.add_event.call_args[0][0]
    assert event_call == "gravity_shift"

    # Gravity is applied in the new random direction
    # Velocity should have increased slightly in a non-zero direction
    assert abs(b.vx) > 0 or abs(b.vy) > 0
