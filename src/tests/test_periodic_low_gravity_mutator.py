from unittest.mock import MagicMock
from ai.game_modes import GAME_MODES
import pytest

def test_periodic_low_gravity_mutator_mode():
    mode = GAME_MODES.get("periodic_low_gravity_mutator")
    assert mode is not None
    assert "low gravity" in mode.name.lower()

    world = MagicMock()
    world.arena = MagicMock()
    world.arena.height = 1000.0
    world.arena.width = 1000.0
    world.arena.hazards = []
    lm = MagicMock()
    lm.data = {"current_season": 1}
    world.leaderboard_manager = lm
    world.weekly_mutator = ""

    # Setup mode
    mode.setup(world, [])
    assert mode.timer == 0.0
    assert mode.low_grav_active == False

    ball1 = MagicMock(alive=True, mass=1.0, _periodic_low_grav_applied=False)


    # Tick 1: Still not active
    mode.apply_dynamic_traits(world, [ball1], 5.0)
    assert mode.low_grav_active == False
    assert "low_gravity" not in mode.mutators

    # Tick 2: Trigger active
    mode.apply_dynamic_traits(world, [ball1], 5.0) # total 10.0
    assert mode.low_grav_active == True
    assert "low_gravity" not in mode.mutators # Will be applied next tick

    # Tick 3: Active
    mode.apply_dynamic_traits(world, [ball1], 5.0)
    assert mode.low_grav_active == True
    assert "low_gravity" in mode.mutators
    assert ball1.is_frictionless == True

    # Tick 4: Deactivate
    mode.apply_dynamic_traits(world, [ball1], 5.0) # total 10.0 active
    assert mode.low_grav_active == False
    assert "low_gravity" not in mode.mutators

def test_periodic_low_gravity_mutator_gd_logic_exists():
    with open("src/ai/game_modes.gd", "r") as f:
        content = f.read()
    assert "class PeriodicLowGravityMutatorMode extends GameMode:" in content
