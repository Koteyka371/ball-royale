import sys
import os

sys.path.insert(0, os.path.abspath('src'))

from ai.game_modes import GAME_MODES, ModifierZonesMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, id_val: int, ball_type: str, x: float, y: float):
        self.id = id_val
        self.ball_type = ball_type
        self.team = ball_type
        self.x = x
        self.y = y
        self.speed = 100.0
        self.base_speed = 100.0
        self.damage = 10.0
        self.base_damage = 10.0
        self.hp = 50.0
        self.max_hp = 100.0
        self.alive = True
        self.mutators = []

def test_modifier_zones_setup():
    mode = GAME_MODES["modifier_zones"]
    assert isinstance(mode, ModifierZonesMode)

    world = MockWorld()
    balls = [
        MockBall(1, "warrior", 500, 500),
        MockBall(2, "spectator", 100, 100)
    ]

    mode.setup(world, balls)

    assert len(mode.zones) == 4
    assert mode.zones[0]["type"] == "speed"
    assert mode.zones[1]["type"] == "damage"
    assert mode.zones[2]["type"] == "heal"
    assert mode.zones[3]["type"] == "debuff"


def test_modifier_zones_tick():
    mode = GAME_MODES["modifier_zones"]
    world = MockWorld()

    # speed zone is at 250, 250
    # damage zone is at 750, 250
    # heal zone is at 500, 750
    # radius is 150

    ball_speed = MockBall(1, "warrior", 250, 250)
    ball_damage = MockBall(2, "warrior", 750, 250)
    ball_heal = MockBall(3, "warrior", 500, 750)
    ball_debuff = MockBall(5, "warrior", 500, 250)
    ball_normal = MockBall(4, "warrior", 900, 900)

    balls = [ball_speed, ball_damage, ball_heal, ball_debuff, ball_normal]

    mode.setup(world, balls)
    mode.tick(world, balls, delta=1.0)

    # speed ball should have 150 speed
    assert ball_speed.speed == ball_speed.base_speed * 1.5
    assert getattr(ball_speed, "zone_modifier_speed", False)

    # damage ball should have 15 damage
    assert ball_damage.damage == ball_damage.base_damage * 1.5
    assert getattr(ball_damage, "zone_modifier_damage", False)

    # heal ball should heal 20 hp
    assert ball_heal.hp == 70.0

    # debuff ball should have halved max_hp and hp capped
    assert ball_debuff.max_hp == 50.0
    assert getattr(ball_debuff, "zone_modifier_debuff", False)
    assert ball_debuff.hp == 50.0

    # normal ball should be unaffected

    assert ball_normal.speed == ball_normal.base_speed
    assert ball_normal.damage == ball_normal.base_damage
    assert ball_normal.hp == 50.0

    # Move speed ball out of zone and tick again
    ball_speed.x = 900
    ball_speed.y = 900
    ball_debuff.x = 900
    ball_debuff.y = 900
    mode.tick(world, [ball_speed, ball_debuff], delta=1.0)

    assert ball_speed.speed == ball_speed.base_speed
    assert not getattr(ball_speed, "zone_modifier_speed", False)
    assert ball_debuff.max_hp == 100.0
    assert not getattr(ball_debuff, "zone_modifier_debuff", False)
