import pytest
import math
from ai.game_modes import QuantumEntanglementMode

class MockArena:
    def __init__(self):
        self.width = 2000.0
        self.height = 2000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.ball_type = "basic"
        self.max_stamina = 100.0
        self.stamina = 100.0
        self.base_speed = 50.0
        self.speed = 50.0
        self.base_damage = 10.0
        self.original_base_damage = 10.0
        self.traits = []
        self.weather_immunity_timer = 0.0
        self.in_mirror_dimension = False
        self.intangible = False
        self.vision_radius = 200.0
        self.invisible = False
        self.speed_multiplier = 1.0
        self.stun_timer = 0.0
        self.burn_timer = 0.0
        self.poison_timer = 0.0
        self.blindness_timer = 0.0
        self.confusion_timer = 0.0
        self.slow_timer = 0.0
        self.frozen_timer = 0.0
        self.silence_timer = 0.0

def test_quantum_entanglement_damage_transfer():
    mode = QuantumEntanglementMode()
    world = MockWorld()

    # Tick once to generate hazards
    mode.tick(world, [], 0.016)

    hazards = [h for h in world.arena.hazards if getattr(h, "kind", "") == "quantum_node"]
    assert len(hazards) == 2

    h1 = hazards[0]
    h2 = hazards[1]

    # Create two balls, one near each hazard
    # Place b1 exactly on h1, b2 exactly on h2
    b1 = MockBall(1, h1.x, h1.y)
    b2 = MockBall(2, h2.x, h2.y)

    balls = [b1, b2]

    # Tick to register initial states
    mode.tick(world, balls, 0.016)

    # Check that previous_states are registered
    assert b1.id in mode.previous_states
    assert b2.id in mode.previous_states

    # Manually reduce HP of b1 by 20 and increase poison by 4.0
    b1.hp = 80.0
    b1.poison_timer = 4.0

    # Next tick should transfer 50% damage and 50% poison to b2
    mode.tick(world, balls, 0.016)

    assert b2.hp == 90.0
    assert b2.poison_timer == 2.0

    # Also verify that the new states are recorded so it doesn't echo back
    assert mode.previous_states[b1.id]["hp"] == 80.0
    assert mode.previous_states[b1.id]["poison_timer"] == 4.0
    assert mode.previous_states[b2.id]["hp"] == 90.0
    assert mode.previous_states[b2.id]["poison_timer"] == 2.0

    # Ensure another tick does nothing since state is synced
    mode.tick(world, balls, 0.016)
    assert b1.hp == 80.0
    assert b2.hp == 90.0
