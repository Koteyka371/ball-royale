import pytest
from unittest.mock import MagicMock

def test_quantum_anomalies_mode_scramble():
    from ai.game_modes import GAME_MODES
    mode = GAME_MODES.get('quantum_anomalies')
    assert mode is not None

    world = MagicMock()
    world.next_id = MagicMock(return_value=123)
    del world.leaderboard_manager
    del world.profile_manager
    world.arena = MagicMock()
    world.arena.width = 1000.0
    world.arena.height = 1000.0
    world.arena.hazards = []

    ball = MagicMock()
    ball.alive = True
    ball.ball_type = "player"
    ball.x = 500.0
    ball.y = 500.0
    ball.radius = 10.0
    ball.speed = 5.0
    ball.damage_multiplier = 1.0
    del ball.quantum_teleport_cooldown
    del ball.quantum_scramble_timer
    del ball.base_speed_scrambled
    del ball.base_radius_scrambled
    del ball.base_damage_mult_scrambled

    # Run setup
    mode.setup(world, [ball])

    # Simulate a tick to spawn anomalies
    mode.tick(world, [ball], 0.016)

    assert len(world.arena.hazards) == 2

    a1 = world.arena.hazards[0]

    # Move ball into anomaly
    ball.x = a1.x
    ball.y = a1.y

    # Simulate a tick to apply scramble
    mode.tick(world, [ball], 0.016)

    # Since speed, radius, and damage_multiplier are scrambled randomly,
    # we just check they have been modified or that base_* are set
    assert hasattr(ball, "base_speed_scrambled")
    assert hasattr(ball, "base_radius_scrambled")
    assert hasattr(ball, "base_damage_mult_scrambled")
    assert ball.quantum_scramble_timer > 0

import unittest.mock

@unittest.mock.patch('random.random', return_value=0.0)
def test_quantum_anomalies_teleport(mock_random):
    from ai.game_modes import GAME_MODES
    mode = GAME_MODES.get('quantum_anomalies')
    assert mode is not None

    world = MagicMock()
    world.next_id = MagicMock(side_effect=[123, 124, 125, 126])
    del world.leaderboard_manager
    del world.profile_manager
    world.arena = MagicMock()
    world.arena.width = 1000.0
    world.arena.height = 1000.0
    world.arena.hazards = []

    ball = MagicMock()
    ball.alive = True
    ball.ball_type = "player"
    ball.radius = 10.0
    ball.speed = 5.0
    ball.damage_multiplier = 1.0
    del ball.quantum_teleport_cooldown
    del ball.quantum_scramble_timer
    del ball.base_speed_scrambled
    del ball.base_radius_scrambled
    del ball.base_damage_mult_scrambled

    # Run setup
    mode.setup(world, [ball])

    # Spawn anomalies
    mode.tick(world, [ball], 0.016)

    a1 = world.arena.hazards[0]
    a2 = world.arena.hazards[1]

    # Place ball exactly at the center of a1 to force a teleport
    ball.x = a1.x
    ball.y = a1.y

    if hasattr(ball, 'quantum_teleport_cooldown'): del ball.quantum_teleport_cooldown
    # Tick to apply teleport
    mode.tick(world, [ball], 0.016)

    # Check if ball moved to a2's position
    print(f'Ball pos: {ball.x}, {ball.y} | A1 pos: {a1.x}, {a1.y} | A2 pos: {a2.x}, {a2.y} | Link 1: {a1.linked_id} | Link 2: {a2.linked_id} | Cooldown: {getattr(ball, "quantum_teleport_cooldown", None)}')
    assert ball.x == a2.x
    assert ball.y == a2.y
    assert ball.quantum_teleport_cooldown > 0
