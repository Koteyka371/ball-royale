import unittest
import math
from ai.game_modes import BloodFogMode
from ai.action import Action

class MockArena:
    def __init__(self):
        self.width = 2000.0
        self.height = 2000.0
        self.hazards = []
        self.is_foggy = False
        self.events = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.events = []

    def add_event(self, event_type, event_data):
        self.events.append((event_type, event_data))

    def get_nearby_entities(self, ball, radius=None):
        return {"boosters": self.boosters, "enemies": [], "allies": [], "hazards": []}

class MockBall:
    def __init__(self):
        self.id = 1
        self.x = 1000.0
        self.y = 1000.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.team = "Red"
        self.speed = 100.0
        self.base_speed = 100.0
        self.vx = 0.0
        self.vy = 0.0
        self.perception_radius = 500.0
        self.is_hologram = False

def test_blood_fog_mode():
    world = MockWorld()
    ball = MockBall()
    mode = BloodFogMode()
    mode.setup(world, [ball])

    assert mode.fog_timer == 15.0
    assert mode.fog_active == False
    assert mode.drain_accumulator == 0.0

    # Tick down to exactly 0 to activate fog, without over-draining
    mode.tick(world, [ball], 15.0)

    assert mode.fog_active == True
    assert world.arena.is_foggy == True

    # At this tick, fog_active became True, so it drained 15.0 * 5.0 = 75.0 HP!
    # Let's reset HP and accumulator for the actual test
    ball.hp = 100.0
    mode.drain_accumulator = 0.0
    world.boosters = []

    # Tick while fog is active to drain HP
    # drain_rate is 5.0, delta is 4.0, total drain is 20.0
    mode.tick(world, [ball], 4.0)

    assert ball.hp == 80.0
    assert len(world.boosters) == 1
    orb = world.boosters[0]
    assert orb.kind == "blood_orb"

    # Now simulate collecting the orb
    action = Action(ball, world)
    action._get_boosters = lambda: [orb]
    action._collect_booster(0.1)

    # HP should heal by 20.0 back to 100.0
    assert ball.hp == 100.0
    assert not orb.active
    assert orb not in world.boosters

if __name__ == "__main__":
    test_blood_fog_mode()
