import pytest
from ai.game_modes import GameMode, GAME_MODES

class MockWorld:
    def __init__(self):
        self.events = []
        self.arena = type("MockArena", (), {"width": 800, "height": 600})()
        self.time = 0.0

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, id_val, x, y, team):
        self.id = id_val
        self.x = x
        self.y = y
        self.radius = 10.0
        self.team = team
        self.alive = True
        self.hp = 50.0
        self.max_hp = 100.0
        self.damage = 20.0
        self.base_damage = 20.0
        self.energy_shield_active = True
        self.energy_shield_hp = 50.0

def test_vip_protection_mode():
    mode = GAME_MODES['vip_protection']
    world = MockWorld()

    # Team 1
    b1 = MockBall(1, 100, 100, 1)
    b2 = MockBall(2, 110, 110, 1) # Close enough to heal
    b3 = MockBall(3, 800, 800, 1) # Too far to heal

    # Team 2
    b4 = MockBall(4, 500, 500, 2)
    b5 = MockBall(5, 510, 510, 2)

    balls = [b1, b2, b3, b4, b5]

    mode.setup(world, balls)
    mode.tick(world, balls, 1.0) # Tick 1 second

    # 1. VIPs selected
    assert len(mode.vips) == 2
    assert 1 in mode.vips
    assert 2 in mode.vips

    # Check team 1 vip
    vip1_id = mode.vips[1]
    vip1 = next(b for b in balls if b.id == vip1_id)
    non_vip1 = next(b for b in balls if b.id != vip1_id and b.team == 1 and b.id != 3)
    far_non_vip1 = b3

    # 2. VIP cannot attack and vulnerable
    assert vip1.damage == 0.0
    assert vip1.energy_shield_active == False

    # 3. Teammates get healed
    assert non_vip1.hp > 50.0 # Heal rate 15, should be 65
    assert far_non_vip1.hp == 50.0 # No heal, too far

    # Tick again
    mode.tick(world, balls, 1.0)
    assert non_vip1.hp > 65.0
