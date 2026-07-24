import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest

from ai.action import Action

class MockHazard:
    def __init__(self, x=0, y=0, radius=20.0, kind="trap", trap_variant=""):
        self.x = x
        self.y = y
        self.radius = radius
        self.kind = kind
        self.trap_variant = trap_variant
        self.duration = 10.0
        self.active = True
        self.id = 999
        self.owner_id = 1

class MockBall:
    def __init__(self, x=0, y=0, radius=10.0, speed=100.0):
        self.id = 2
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = speed
        self.base_speed = speed
        self.stun_timer = 0.0
        self.alive = True
        self.is_intangible = False
        self.bounces_left = 0
        self.vx = 0.0
        self.vy = 0.0
        self.state_history = []
        self.max_hp = 100
        self.hp = 100
        self.perception_radius = 500.0
        self.fast_motion_zone_active = False
        self.slow_motion_zone_active = False
        self.stamina = 100

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards
        self.rect = {"x": -1000, "y": -1000, "w": 2000, "h": 2000}
        self.active_weather = None

class MockWorld:
    def __init__(self, balls, arena):
        self.balls = balls
        self.arena = arena
        self.events = []
        self.rules = {}

    def get_nearby_entities(self, *args, **kwargs):
        return {"projectiles": [], "boosters": [], "hazards": self.arena.hazards, "enemies": []}

    def check_collision(self, *args, **kwargs):
        return None

    def spawn_projectile(self, *args, **kwargs):
        pass

def test_grapple_trap_triggers_and_roots():
    trap = MockHazard(x=100, y=100, radius=40.0, kind="grapple_trap")
    trap.owner_id = 1

    # Victim is within the 200 range (dist_sq < 40000)
    victim = MockBall(x=150, y=100) # distance = 50
    victim.speed = 0 # Prevent wander so we test exact physics

    world = MockWorld([victim], MockArena([trap]))

    action = Action(victim, world)

    # 1 tick to pull
    action.execute("idle", 0.1)

    # Check if pulled
    assert victim.x < 150 # Moved towards 100

    # Should not be rooted yet (if distance > radius)

    # Move exactly onto center
    victim.x = 105
    action.execute("idle", 0.1)

    # Should root for 2 seconds and destroy trap
    assert victim.stun_timer >= 2.0
    assert trap.duration == 0.0
