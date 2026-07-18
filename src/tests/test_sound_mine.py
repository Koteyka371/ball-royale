import pytest
from unittest.mock import MagicMock
from ai.action import Action

def test_sound_mine_noisy_skill():
    world = MagicMock()
    world.arena = MagicMock()

    # Create dynamic Hazard
    mine = type('Hazard', (), {'id': 1, 'x': 100, 'y': 100, 'radius': 50.0, 'kind': "sound_mine", 'active': True})()
    world.arena.hazards = [mine]

    ball = type('MockEntity', (), {'id': 100, 'x': 110, 'y': 110, 'radius': 20.0, 'hp': 100, 'ball_type': 'basic', 'vx': 0.0, 'vy': 0.0, 'suspended_projectiles': [], 'state_history': [], 'last_teleport_tick': -100})()
    ball.skill = "dash"
    ball.skill_timer = 0.0

    world.next_id = 9999
    world.balls = [ball]

    action = Action(ball, world)
    action._use_skill()

    # Should explode because dash is noisy
    assert not getattr(mine, "active", True)
    assert getattr(mine, "is_exploded", False)

def test_sound_mine_quiet_skill():
    world = MagicMock()
    world.arena = MagicMock()

    mine = type('Hazard', (), {'id': 1, 'x': 100, 'y': 100, 'radius': 50.0, 'kind': "sound_mine", 'active': True})()
    world.arena.hazards = [mine]

    ball = type('MockEntity', (), {'id': 100, 'x': 110, 'y': 110, 'radius': 20.0, 'hp': 100, 'ball_type': 'basic', 'vx': 0.0, 'vy': 0.0, 'suspended_projectiles': [], 'state_history': [], 'last_teleport_tick': -100})()
    ball.skill = "heal"
    ball.skill_timer = 0.0

    world.next_id = 9999
    world.balls = [ball]

    action = Action(ball, world)
    action._use_skill()

    # Should not explode because heal is not noisy
    assert getattr(mine, "active", True)
    assert not getattr(mine, "is_exploded", False)
