import pytest
from ai.action import Action
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
        self.suspended_projectiles = []
        self.state_history = []
        self.last_teleport_tick = -100
        for k, v in kwargs.items():
            setattr(self, k, v)

class MockHazard:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", random.randint(1000, 9999))
        self.kind = "moving_wall"
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

def test_kinetic_shield_moving_wall_collision():
    from ai.game_modes import BattleRoyaleMode
    world = MockWorld()
    b = MockEntity(x=10, y=0, vx=-100, kinetic_shield_active=True, speed_boost_timer=0, shielding=0)
    world.balls.append(b)

    h = MockHazard(x=0, y=0, radius=20, vx=0, vy=0)
    world.arena.hazards.append(h)

    gm = BattleRoyaleMode()
    gm.obstacle_timer = 0
    gm.random_event_timer = 0

    # In GameMode.tick, the signature is def tick(self, world: 'Any', balls: 'List[Any]', delta: float) -> None:
    # Actually wait, let me look at GameMode tick:
    # `def tick(self, world: 'Any', delta: float) -> None:` Wait, game_modes.py line 1102 says apply_dynamic_traits(world, balls, delta)
    # Let me use the correct signature
    gm.tick(world, world.balls, 0.1)

    # We expect speed boost and shielding to increase
    assert b.speed_boost_timer > 0.0
    assert b.shielding > 0.0
    assert b.vx == 50.0

def test_kinetic_shield_stored_damage_buff_knockback():
    world = MockWorld()
    b1 = MockEntity(id=1, x=0, y=0, vx=0, vy=0, kinetic_shield_active=False, kinetic_shield_stored_damage=100.0, speed_boost_timer=0, speed=200.0, base_speed=200.0)
    b2 = MockEntity(id=2, x=10, y=0, vx=0, vy=0)
    world.balls.extend([b1, b2])

    action = Action(b1, world)

    # We trigger the melee attack
    # _attempt_damage_internal triggers the logic we just patched
    action._attempt_damage_internal(b1, b2)

    # b1 should get speed boost
    assert b1.speed_boost_timer == 3.0
    assert b1.speed == 200.0 + 100.0 + (100.0 * 2.0)
    assert b1.kinetic_shield_active == False
    assert b1.kinetic_shield_stored_damage == 0.0

    # b2 should get knockback
    # knockback_force = 1000.0 + stored_dmg * 50.0 = 1000.0 + 5000.0 = 6000.0
    # direction is from b1(0,0) to b2(10,0) -> nx=1, ny=0
    # b2.vx should be 6000.0
    assert b2.vx == 6000.0
    assert b2.vy == 0.0
    assert b2._knockback_timer == 0.5
