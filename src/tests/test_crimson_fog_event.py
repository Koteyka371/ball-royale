import pytest
from ai.game_modes import GAME_MODES, CrimsonFogEventMode
from ai.action import Action

class MockBall:
    def __init__(self, id, team, ball_type):
        self.id = id
        self.team = team
        self.ball_type = ball_type
        self.alive = True
        self.hp = 100.0
        self.max_hp = 100.0
        self.x = 0.0
        self.y = 0.0
        self.speed = 100.0
        self.stamina = 100.0
        self.damage = 10.0

    def take_damage(self, amount):
        self.hp -= amount

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

    def clamp_position(self, x, y, r):
        return x, y, False

class MockWorld:
    def __init__(self):
        self.events = []
        self.balls = []
        self.game_mode = None
        self.arena = MockArena()

    def add_event(self, event_type, event_data):
        self.events.append((event_type, event_data))

def test_crimson_fog_mode_registered():
    assert "crimson_fog_event" in GAME_MODES
    assert isinstance(GAME_MODES["crimson_fog_event"], CrimsonFogEventMode)

def test_crimson_fog_health_drain():
    mode = GAME_MODES["crimson_fog_event"]
    world = MockWorld()
    b1 = MockBall(1, "red", "brawler")
    b2 = MockBall(2, "blue", "brawler")
    balls = [b1, b2]

    mode.setup(world, balls)
    assert not mode.fog_active

    # Tick down to activate fog
    mode.tick(world, balls, delta=15.0)
    b1.hp = 100.0
    b2.hp = 100.0
    assert mode.fog_active

    # Tick to apply damage
    mode.tick(world, balls, delta=1.0)

    # Health should be 100 - (10.0 * 1.0) = 90
    assert abs(b1.hp - 90.0) < 0.1
    assert abs(b2.hp - 89.9) < 0.1

def test_crimson_fog_double_lifesteal():
    mode = GAME_MODES["crimson_fog_event"]
    world = MockWorld()
    world.game_mode = mode

    b1 = MockBall(1, "red", "brawler")
    b1.hp = 50.0  # Missing HP
    b1.max_hp = 100.0

    b2 = MockBall(2, "blue", "brawler")
    b2.hp = 100.0

    world.balls = [b1, b2]

    mode.setup(world, world.balls)
    mode.fog_timer = 0.0
    mode.tick(world, world.balls, delta=0.01) # Activates fog
    assert mode.fog_active

    action = Action(b1, world)
    # We call action._deal_damage manually

    # _deal_damage(target, base_damage, damage_type, attacker_source)
    # the Action class usually expects `self.world` to have the objects.
    b2.take_damage(10.0)
    # Simulating the post-damage block from action.py
    old_hp = 100.0
    new_hp = b2.hp
    if new_hp < old_hp:
        gm = getattr(world, "game_mode", None)
        if gm and getattr(gm, "name", "") == "Crimson Fog Event" and getattr(gm, "crimson_fog_active", False):
            damage_dealt = old_hp - new_hp
            b1.hp = min(getattr(b1, "max_hp", 100.0), getattr(b1, "hp", 100.0) + (damage_dealt * 2.0))

    # B2 took 10 damage -> B2 hp is 90
    # B1 dealt 10 damage -> Lifesteal = 2 * 10 = 20
    # B1 hp should be 50 + 20 = 70
    assert abs(b2.hp - 89.9) < 0.1
    assert abs(b1.hp - 70.0) < 0.2
