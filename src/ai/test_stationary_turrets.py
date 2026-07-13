import pytest
from ai.game_modes import StationaryTurretsMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

class MockBall:
    def __init__(self, id_val, x, y, team):
        self.id = id_val
        self.x = x
        self.y = y
        self.team = team
        self.alive = True
        self.hp = 100.0

def test_stationary_turrets_mode():
    mode = StationaryTurretsMode()
    world = MockWorld()

    # Spawn a turret manually to test interaction
    mode.spawn_timer = 20.0
    mode.tick(world, [], 0.1)

    assert len(mode.turrets) == 1
    t = mode.turrets[0]
    t.x = 500
    t.y = 500
    t.radius = 80

    # Add a ball from Team 1 inside radius
    b1 = MockBall(1, 500, 500, "Team A")
    balls = [b1]

    # Tick should progress capture
    mode.tick(world, balls, 0.5)
    # 20.0 * 0.5 = 10.0 progress? Initially t.team is None.
    # When t.team != occupying_team, progress goes down by 20*delta.
    # Wait, if t.team is None and progress=0, it goes to -10, which is <=0, so it gets captured.
    assert t.team == "Team A"
    assert t.capture_progress >= 0.0

    # Move capture progress up
    t.capture_progress = 90.0
    mode.tick(world, balls, 0.5)
    assert t.capture_progress == 100.0

    # Now add an enemy within attack range
    b2 = MockBall(2, 600, 500, "Team B")
    b2.hp = 100.0
    balls.append(b2)

    # Advance time so turret shoots
    t.fire_timer = 1.0
    mode.tick(world, balls, 0.1)

    assert b2.hp == 100.0 - t.damage

    # If both teams inside, capture progress shouldn't increase for either
    t.capture_progress = 50.0
    b2.x = 520
    b2.y = 500
    mode.tick(world, balls, 0.1)
    assert t.capture_progress == 50.0
