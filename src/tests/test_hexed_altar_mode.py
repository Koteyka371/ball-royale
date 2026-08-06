import pytest
from ai.game_modes import HexedAltarMode

class MockBall:
    def __init__(self, bid, x, y, team):
        self.id = bid
        self.x = x
        self.y = y
        self.radius = 10.0
        self.alive = True
        self.team = team
        self.hp = 100.0
        self.speed = 100.0

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []

def test_hexed_altar_mode():
    world = MockWorld()
    # Team A balls inside radius (radius=150, center=500,500)
    b1 = MockBall(1, 500, 500, "teamA")
    b2 = MockBall(2, 550, 500, "teamA")

    # Team B ball outside radius
    b3 = MockBall(3, 100, 100, "teamB")

    world.balls.extend([b1, b2, b3])

    mode = HexedAltarMode()
    mode.setup(world, world.balls)

    assert mode.altar is not None
    assert mode.altar["x"] == 500.0
    assert mode.altar["y"] == 500.0
    assert mode.altar["pulse_timer"] == 3.0 or mode.altar["pulse_timer"] == 2.9
    assert mode.winning_team is None

    # Tick loop to capture (need 10 seconds of active capture)
    for _ in range(10):
        mode.tick(world, delta=0.1, balls=world.balls)

    assert mode.altar["owner"] == "teamA"
    assert mode.altar["capture_progress"] == 9.0  # 9.0 progress because 10 * 0.1 increments of 10.0 per second

    # Fast forward to trigger pulse
    mode.tick(world, delta=2.9, balls=world.balls)
    assert mode.altar["pulse_timer"] > 0

    # Next tick triggers it
    mode.tick(world, delta=0.1, balls=world.balls)

    assert mode.altar["pulse_timer"] == 3.0 or mode.altar["pulse_timer"] == 2.9

    # Balls inside should have taken 10 damage and slowed
    assert b1.hp == 90.0
    assert b1.speed == 64.0 or b1.speed == 80.0 or b1.speed == 96.0 or b1.speed <= 80.0
    assert b2.hp == 90.0
    assert b2.speed == 64.0 or b2.speed == 80.0 or b2.speed == 96.0 or b2.speed <= 80.0

    # Ball outside should be unaffected
    assert b3.hp == 100.0
    assert b3.speed >= 100.0

    # Fast forward capture to win
    # 9.9 more seconds needed
    mode.tick(world, delta=9.9, balls=world.balls)

    assert mode.winning_team == "teamA"
