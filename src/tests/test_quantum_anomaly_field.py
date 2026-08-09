import pytest
from unittest.mock import MagicMock
from ai.game_modes import GAME_MODES

def test_quantum_anomaly_field_tick():
    mode = GAME_MODES.get("quantum_anomaly_field")
    assert mode is not None

    world = MagicMock()
    world.arena.width = 1000
    world.arena.height = 1000

    b = MagicMock()
    b.alive = True
    b.ball_type = "player"
    b.x = 500
    b.y = 500
    b.base_speed_multiplier = 1.0
    b.base_damage_multiplier = 1.0
    b.base_mass = 1.0
    b.in_quantum_anomaly = False

    # Tick to spawn anomalies
    mode.tick(world, [b], 6.0)

    assert len(mode.anomalies) >= 2

    # Force anomaly position to ball position
    mode.anomalies[0]["x"] = 500
    mode.anomalies[0]["y"] = 500
    mode.anomalies[0]["radius"] = 100

    mode.tick(world, [b], 0.1)

    assert b.in_quantum_anomaly
    assert hasattr(b, "original_speed_multiplier")
    assert b.original_speed_multiplier == 1.0

    # Move ball out of anomaly
    b.x = 100
    b.y = 100

    mode.tick(world, [b], 0.1)

    assert not b.in_quantum_anomaly
    assert b.base_speed_multiplier == 1.0
