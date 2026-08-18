import pytest
from ai.game_modes import DangerBeaconMode

class MockHazard:
    def __init__(self, kind, x, y, radius, owner_id, owner_team):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = radius
        self.owner_id = owner_id
        self.owner_team = owner_team

class MockBall:
    def __init__(self, ball_id, team, x, y, hp=100):
        self.id = ball_id
        self.team = team
        self.x = x
        self.y = y
        self.radius = 20.0
        self.hp = hp
        self.minimap_ping_timer = 0.0

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, type, data):
        self.events.append({'type': type, 'data': data})

def test_danger_beacon_mode():
    mode = DangerBeaconMode()
    world = MockWorld()

    owner = MockBall("owner1", "team1", 0, 0)
    ally = MockBall("ally1", "team1", 10, 10)
    enemy_inside = MockBall("enemy1", "team2", 50, 0)
    enemy_outside = MockBall("enemy2", "team2", 200, 0)

    balls = [owner, ally, enemy_inside, enemy_outside]

    # Create beacon at (0, 0) with radius 100
    beacon = MockHazard("danger_beacon", 0, 0, 100, "owner1", "team1")
    world.arena.hazards.append(beacon)

    # Tick 1: enemy_inside should get a ping
    mode.tick(world, balls, 0.1)

    # Check events
    assert len(world.events) == 1
    event = world.events[0]
    assert event['type'] == 'minimap_ping'
    assert event['data']['x'] == 50
    assert event['data']['y'] == 0
    assert event['data']['color'] == 'red'
    assert event['data']['duration'] == 0.5

    # Owner, ally, enemy_outside shouldn't have their timer set
    assert owner.minimap_ping_timer == 0.0
    assert ally.minimap_ping_timer == 0.0
    assert enemy_outside.minimap_ping_timer == 0.0

    # enemy_inside should have its timer set to 1.0
    assert enemy_inside.minimap_ping_timer == 1.0

    # Tick 2: timer is 1.0, so it decreases by delta (0.1), no new ping
    mode.tick(world, balls, 0.1)

    assert len(world.events) == 1  # Still 1
    assert enemy_inside.minimap_ping_timer == 1.0 - 0.1

    # Loop until timer reaches 0
    for _ in range(9):
        mode.tick(world, balls, 0.1)

    # Timer should be 0 now
    assert enemy_inside.minimap_ping_timer <= 1e-5

    # Next tick triggers another ping
    mode.tick(world, balls, 0.1)
    assert len(world.events) == 2
    assert enemy_inside.minimap_ping_timer == 1.0
