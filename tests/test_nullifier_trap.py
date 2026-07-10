import sys
import os
sys.path.insert(0, os.path.abspath('src'))
from ai.action import Action
import math

class MockEntity:
    def __init__(self, id, x, y, kind="trap", trap_variant="nullifier", radius=15.0):
        self.id = id
        self.x = x
        self.y = y
        self.kind = kind
        self.trap_variant = trap_variant
        self.duration = 5.0
        self.radius = radius
        self.active = True

    def get(self, key, default=None):
        return getattr(self, key, default)

class MockBall:
    def __init__(self, id, x=0, y=0, team="team1"):
        self.id = id
        self.team = team
        self.x = x
        self.y = y
        self.radius = 10
        self.speed = 10
        self.base_speed = 10
        self.hp = 100
        self.max_hp = 100
        self.stamina = 100
        self.alive = True
        self.ball_type = "basic"
        self.perception_radius = 250.0

        # Shields
        self.reflect_shield_active = True
        self.energy_shield_active = True
        self.shield_booster_active = True

        # Buffs
        self.speed_buff_timer = 5.0
        self.emp_immunity_timer = 5.0
        self.speed_booster_timer = 5.0

    def get(self, key, default=None):
        return getattr(self, key, default)

class MockWorld:
    def __init__(self):
        self.balls = []
        self.boosters = []
        self.arena = type('MockArena', (), {'hazards': [], 'update_zone': lambda *args: None, 'width': 1000, 'height': 1000, 'clamp_position': lambda self, x, y, r: (x, y, False)})()

    def get_nearby_entities(self, ball, radius):
        return {
            "enemies": [b for b in self.balls if b.team != ball.team],
            "allies": [],
            "boosters": self.boosters
        }

def test_nullifier_trap():
    ball = MockBall(1, 0, 0)
    enemy1 = MockBall(2, 100, 100, "team2")  # Inside radius
    enemy2 = MockBall(3, 3000, 3000, "team2") # Outside radius

    world = MockWorld()
    world.balls = [ball, enemy1, enemy2]

    trap = MockEntity(10, 5, 5, kind="trap", trap_variant="nullifier")
    world.arena.hazards = [trap]

    action = Action(ball, world)
    action.execute("idle", 1.0)

    # Ball stepped on it
    # Shields should be gone for ball and enemy1
    assert not ball.reflect_shield_active
    assert not ball.energy_shield_active
    assert not enemy1.reflect_shield_active
    assert not enemy1.speed_buff_timer

    # enemy2 is far away, so it should keep its shields
    assert enemy2.reflect_shield_active
    assert enemy2.energy_shield_active
    assert enemy2.speed_buff_timer == 5.0

    # trap should be destroyed
    assert trap.duration == 0.0

if __name__ == "__main__":
    test_nullifier_trap()
    print("Test passed!")
