import sys
import os
sys.path.insert(0, os.path.abspath('src'))
from ai.action import Action

class MockEntity:
    def __init__(self, x=0, y=0, kind="trap", radius=15.0, hp=100.0, alive=True, damage=0.0):
        self.damage = damage
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = radius
        self.hp = hp
        self.alive = alive
        self.id = 999
        self.team = "test_team"
        self.ball_type = "booster"

    def get(self, key, default=None):
        return getattr(self, key, default)

class MockBall(MockEntity):
    def __init__(self, x=0, y=0, radius=10.0, hp=100.0, alive=True):
        super().__init__(x, y, "ball", radius, hp, alive)
        self.has_thermal_vision = True
        self.inventory = ["thermal_goggles", "advanced_optics", "stealth_drone"]
        self.advanced_optics_active = True
        self.has_stealth_drone = True
        self.ball_type = "basic"

class MockArena:
    def __init__(self):
        self.hazards = []

    def update_zone(self, tick, delta=None):
        pass

    def clamp_position(self, x, y, radius=0):
        return x, y, False

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.balls = []
        self.next_id = 1000

    def add_event(self, event_type, data):
        pass

    def get_nearby_entities(self, ball, radius):
        return {
            "enemies": [b for b in self.balls if b.team != ball.team],
            "allies": [],
            "boosters": self.boosters
        }

def test_emp_blast_trap():
    ball = MockBall(x=100, y=100)
    world = MockWorld()
    world.balls.append(ball)

    trap = MockEntity(x=105, y=100, kind="trap")
    trap.trap_variant = "emp_blast"
    trap.duration = 10.0
    trap.armed = True
    world.arena.hazards.append(trap)

    action = Action(ball, world)
    action.execute("idle", 0.1)

    assert ball.has_thermal_vision == False
    assert "thermal_goggles" not in ball.inventory
    assert ball.advanced_optics_active == False
    assert "advanced_optics" not in ball.inventory
    assert ball.has_stealth_drone == False
    assert "stealth_drone" not in ball.inventory
    assert trap.duration == 0.0

if __name__ == "__main__":
    test_emp_blast_trap()
    print("Passed.")
