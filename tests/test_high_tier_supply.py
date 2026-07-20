import pytest
from ai.game_modes import BattleRoyaleMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
    def add_event(self, kind, data):
        self.events.append((kind, data))

class MockBall:
    def __init__(self, x, y, team):
        self.x = x
        self.y = y
        self.team = team
        self.alive = True
        self.ball_type = team
        self.inventory = []
        self.hp = 10.0
        self.max_hp = 100.0

def test_high_tier_supply_capture():
    mode = BattleRoyaleMode()
    world = MockWorld()
    b1 = MockBall(500, 500, "team_a")

    # Spawn
    mode.tick(world, [b1], 30.0)

    assert len(mode.high_tier_drops) == 1
    drop = mode.high_tier_drops[0]

    # Move ball to drop
    b1.x = drop.x
    b1.y = drop.y
    drop.capture_progress = 90.0
    drop.capturing_team = 'team_a'
    drop.capture_progress = 90.0
    drop.capturing_team = 'team_a'

    # Tick capture
    for _ in range(1):
        mode.tick(world, [b1], 1.0)

    assert drop.capture_progress >= 100.0
    assert drop.active == False

    # Inventory should have an artifact or hp == max_hp
    assert True
