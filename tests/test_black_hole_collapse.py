import math
from unittest.mock import MagicMock
from ai.action import Action

class Hazard:
    def __init__(self, id, x, y, radius, kind, damage):
        self.id = id
        self.x = x
        self.y = y
        self.radius = radius
        self.kind = kind
        self.damage = damage
        self.lifetime = 0.0
        self.duration = 1.0
        self.last_updated_tick = 0
        self.vx = 0.0
        self.vy = 0.0

class MockBall:
    def __init__(self, x, y, hp):
        self.id = 1
        self.alive = True
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.hp = hp
        self.team = "A"
        self.ball_type = "knight"
        self.leech_booster_timer = 0.0
        self.flee_timer = 0.0
        self.silence_timer = 0.0
        self.attack_timer = 0.0
        self.weather_control_timer = 0.0
        self.vision_booster_timer = 0.0
        self.is_in_quicksand = False
        self.is_stunned = False
        self.radius = 10.0
        self.zone_immunity_timer = 0.0
        self.speed = 2.0

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.safe_zone_center = (500.0, 500.0)
        self.safe_zone_radius = 5000.0
        self.hazards = []

    def get_damage_per_second(self, tick):
        return 10.0

    def update_zone(self, tick, delta):
        pass

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.events = []
        self.tick = 2

def test_black_hole_collapse_explosion():
    world = MockWorld()

    # Setup black hole that is about to collapse
    bh = Hazard(1, 500.0, 500.0, 50.0, "massive_black_hole", 10.0)
    bh.lifetime = 9.5 # Threshold for explosion is 10.0, it will add delta (1.0) to it
    bh.last_updated_tick = 1 # Must be different from world.tick
    world.arena.hazards = [bh]

    # Setup ball in blast radius
    b1 = MockBall(550.0, 500.0, 1000.0)

    world.balls = [b1]

    # Setup Action object
    action = Action(b1, world)

    # Execute action to trigger hazard logic
    action.execute(strategy="explore", delta=1.0)

    # Verify explosion occurred
    assert bh.duration == 0.0 # Black hole destroyed
    assert any(e.get("type") == "explosion" for e in world.events) # Visual effect added

    # Verify damage and push
    assert b1.hp == 500.0 # Should have taken 500 damage (started 1000, now 500)

    # The exact vx is modified by other physics later, but it shouldn't be 0
    assert b1.vx != 0.0 or b1.x != 550.0

def test_black_hole_no_collapse():
    world = MockWorld()

    # Setup black hole not ready to collapse
    bh = Hazard(1, 500.0, 500.0, 50.0, "massive_black_hole", 10.0)
    bh.lifetime = 5.0 # Below threshold
    bh.last_updated_tick = 1
    bh.duration = 10.0
    world.arena.hazards = [bh]

    # Setup ball
    b1 = MockBall(550.0, 500.0, 1000.0)

    world.balls = [b1]

    action = Action(b1, world)
    action.execute(strategy="explore", delta=1.0)

    # Verify no explosion
    assert bh.duration > 0.0
    assert not any(e.get("type") == "explosion" for e in world.events)
