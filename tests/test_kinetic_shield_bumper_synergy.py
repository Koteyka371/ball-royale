import pytest
import math
from src.ai.action import Action
import random

class MockEntity:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", random.randint(1000, 9999))
        self.hp = 100.0
        self.ball_type = "basic"
        self.vx = 0.0
        self.vy = 0.0
        self.x = 0.0
        self.y = 0.0
        self.radius = 10.0
        self.mass = 1.0
        self.shielding = 0.0
        self.speed_boost_timer = 0.0
        self.suspended_projectiles = []
        self.state_history = []
        self.last_teleport_tick = -100
        for k, v in kwargs.items():
            setattr(self, k, v)

class MockHazard:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", random.randint(1000, 9999))
        self.kind = "bumper"
        self.x = 0.0
        self.y = 0.0
        self.radius = 10.0
        self.active = True
        self.vx = 0.0
        self.vy = 0.0
        for k, v in kwargs.items():
            setattr(self, k, v)

class MockArena:
    def __init__(self):
        self.hazards = []
    def clamp_position(self, x, y, r):
        return (x, y, False)
    def update_zone(self, tick, delta):
        pass

class MockWorld:
    def __init__(self):
        self.next_id = 9999
        self.hazards = []
        self.balls = []
        self.arena = MockArena()
        self.tick = 0
        self.events = []

def test_kinetic_shield_bumper_synergy_juggernaut():
    """
    Test that when a ball hits a bumper with both kinetic shield and bumper synergy active,
    it gains bonus shield capacity and mass (juggernaut state), but NO speed boost.
    """
    world = MockWorld()

    # Setup ball near bumper (within collision range)
    # Give both active buffs
    b = MockEntity(
        x=15.0,
        y=0.0,
        vx=-100.0,
        kinetic_shield_active=True,
        bumper_synergy_active=True,
        shielding=0.0,
        speed_boost_timer=0.0,
        mass=1.0,
        base_mass=1.0
    )
    world.balls.append(b)

    # Setup bumper at origin
    h = MockHazard(x=0.0, y=0.0, radius=20.0, kind="bumper")
    world.arena.hazards.append(h)

    action = Action(b, world)

    # Execute action loop (which will trigger bumper collision logic)
    action.execute("idle", 0.1)

    # 1. Shielding should have increased more than baseline
    assert b.shielding > 0.0

    # 2. Mass should have increased (Juggernaut)
    assert b.mass > 1.0

    # 3. No speed boost should have been applied (unlike the normal interaction)
    assert b.speed_boost_timer == 0.0

def test_kinetic_shield_bumper_no_synergy():
    """
    Test normal kinetic shield + bumper interaction (NO bumper synergy).
    It should grant shielding AND a speed boost, but NO mass increase.
    """
    world = MockWorld()

    # Setup ball near bumper
    # Give ONLY kinetic shield
    b = MockEntity(
        x=15.0,
        y=0.0,
        vx=-100.0,
        kinetic_shield_active=True,
        bumper_synergy_active=False,
        shielding=0.0,
        speed_boost_timer=0.0,
        mass=1.0,
        base_mass=1.0
    )
    world.balls.append(b)

    h = MockHazard(x=0.0, y=0.0, radius=20.0, kind="bumper")
    world.arena.hazards.append(h)

    action = Action(b, world)
    action.execute("idle", 0.1)

    # 1. Shielding should have increased
    assert b.shielding > 0.0

    # 2. Speed boost SHOULD be applied
    assert b.speed_boost_timer > 0.0

    # 3. Mass should remain base value
    assert b.mass == 1.0
