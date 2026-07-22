from ai.ball_types_necromancer import Necromancer
from ai.test_action_advanced import MockBall, MockWorld
import pytest

def test_necromancer_lich_evolution():
    world = MockWorld()
    necro = Necromancer(1, 0.0, 0.0)
    necro._cached_world = world

    minion = MockBall()
    minion.id = 2
    minion.minion_owner = 1
    minion.ball_type = "minion"
    minion.alive = True
    minion.base_speed = 2.0
    minion.base_damage = 10.0
    minion.speed = 2.0
    minion.damage = 10.0

    world.balls = [necro, minion]

    # Tick for 60 seconds without taking damage
    necro.tick(60.1)

    # Check if evolved
    assert necro.is_lich == True
    assert necro.BALL_TYPE == "lich"

    # Check if minion enraged
    assert getattr(minion, "is_enraged", False) == True
    assert minion.enrage_timer == 99999.0

    # Check if dragons spawned
    dragons = [b for b in world.balls if getattr(b, "ball_type", "") == "skeletal_dragon"]
    assert len(dragons) == 2
    for d in dragons:
        assert getattr(d, "has_ranged_breath", False) == True
        assert getattr(d, "is_enraged", False) == True
        assert d.enrage_timer == 99999.0

def test_necromancer_lich_evolution_interrupted_by_damage():
    world = MockWorld()
    necro = Necromancer(1, 0.0, 0.0)
    necro._cached_world = world

    # Tick for 30 seconds
    necro.tick(30.0)

    # Take damage
    necro.take_damage(10.0)
    assert necro.survival_without_damage == 0.0

    # Tick for another 35 seconds
    necro.tick(35.0)

    # Shouldn't be lich yet
    assert necro.is_lich == False
    assert necro.BALL_TYPE == "necromancer"

    # Tick for 26 more seconds (total 61 since damage)
    necro.tick(26.0)

    # Now it should be a lich
    assert necro.is_lich == True
    assert necro.BALL_TYPE == "lich"
