import pytest
from ai.game_modes import InfiltrationMode

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.events = []
        self.alarm_triggered = False

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, id=1, ball_type="player"):
        self.id = id
        self.ball_type = ball_type
        self.x = 500.0
        self.y = 500.0
        self.radius = 10.0
        self.stealth_booster_timer = 0.0
        self.last_skill_timer = 0.0
        self.reveal_timer = 0.0
        self.skill_timer = 0.0

def test_infiltration_vaults():
    mode = InfiltrationMode()
    world = MockWorld()
    ball = MockBall()

    # 1. Setup should spawn 3 vaults
    mode.setup(world, [ball])
    vaults = [h for h in world.arena.hazards if getattr(h, "kind", "") == "vault"]
    assert len(vaults) == 3
    assert all(getattr(v, "health", 0) == 300.0 for v in vaults)

    # Check that infiltration still works
    assert ball.stealth_booster_timer == 9999.0

    # 2. Tick should not destroy healthy vaults
    mode.tick(world, [ball], 0.1)
    vaults = [h for h in world.arena.hazards if getattr(h, "kind", "") == "vault"]
    assert len(vaults) == 3

    # 3. Destroy a vault
    vaults[0].health = 0
    mode.tick(world, [ball], 0.1)

    # Check that the vault is gone and loot appeared
    new_vaults = [h for h in world.arena.hazards if getattr(h, "kind", "") == "vault"]
    assert len(new_vaults) == 2

    loots = [h for h in world.arena.hazards if getattr(h, "kind", "") == "legendary_loot"]
    assert len(loots) == 1

    # Check that loot is in boosters as well
    booster_loots = [b for b in world.boosters if getattr(b, "kind", "") == "legendary_loot"]
    assert len(booster_loots) == 1

    # Check that event was triggered
    assert any(e[0] == "vault_opened" for e in world.events)
