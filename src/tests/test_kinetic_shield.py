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
