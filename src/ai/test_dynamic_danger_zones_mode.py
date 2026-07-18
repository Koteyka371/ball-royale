import math
import pytest
from ai.game_modes import GameMode, GAME_MODES
from ai.game_modes import DynamicDangerZonesMode

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []
        self.weather = "clear"

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.next_id = 1
        self.dead_balls = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.ball_type = "basic"
        self.team = "A"

    def take_damage(self, dmg):
        self.hp -= dmg

def test_dynamic_danger_zones_mode():
    mode = DynamicDangerZonesMode()
    world = MockWorld()
    balls = [MockBall(1, 500, 500)]
    mode.setup(world, balls)

    # Tick loop to simulate real time
    for _ in range(600): # 6 seconds
        mode.tick(world, balls, 0.01)

    assert len(mode.zones) >= 1

    # The zone isn't active yet, shouldn't damage balls
    balls[0].hp = 100.0
    balls[0].x = mode.zones[0]["x"]
    balls[0].y = mode.zones[0]["y"]

    mode.tick(world, balls, 0.01)

    assert balls[0].hp == 100.0

    # Tick another 500 frames to make the warning delay finish
    for _ in range(500):
        mode.tick(world, balls, 0.01)

    assert mode.zones[0]["active"]

    # Now it should damage the ball
    balls[0].x = mode.zones[0]["x"]
    balls[0].y = mode.zones[0]["y"]
    mode.tick(world, balls, 0.01)

    assert balls[0].hp < 100.0

    # Verify active zone shrinks over its duration
    active_zone_radius_before = mode.zones[0]["radius"]
    mode.tick(world, balls, 0.01)
    assert mode.zones[0]["radius"] < active_zone_radius_before

    # Verify spawn zone radius shrinks as match time progresses
    mode.setup(world, balls)
    for _ in range(600): # 6 seconds
        mode.tick(world, balls, 0.01)

    initial_radius = mode.zones[0]["radius"]
    assert initial_radius <= 200.0 # base radius

    # Fast forward to 150 seconds
    for _ in range(15000):
        mode.tick(world, balls, 0.01)

    # By 150s, the current max radius logic applies to new zones
    # Note: `tick` increments the match time, and whenever it spawns a zone, it sets the radius
    # The current zone should be around 50% of the original radius
    # Find the newest zone
    assert len(mode.zones) >= 1
    shrunk_radius = mode.zones[-1]["radius"]
    assert shrunk_radius < initial_radius
