import math
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.action import Action

class MockBall:
    def __init__(self, x=50, y=50, team="red", ball_type="generic"):
        self.id = 1
        self.x = x
        self.y = y
        self.team = team
        self.ball_type = ball_type
        self.hp = 100
        self.max_hp = 100
        self.alive = True
        self.is_illusion = False
        self.illusion_timer = 0
        self.skill = "deploy_illusion"
        self.skill_timer = 0
        self.speed = 10
        self.damage = 10
        self.perception_radius = 200
        self.vx = 0
        self.vy = 0

class MockWorld:
    def __init__(self):
        self.balls = []
        self.next_id = 100
        self.events = []
    def get_nearby_entities(self, ball, radius):
        return [b for b in self.balls if b != ball]

def test_mimic_cascade():
    world = MockWorld()
    clone = MockBall(50, 50, "red")
    clone.id = 1
    clone.is_mimic_charging = True
    clone.hp = 50.0
    clone.max_hp = 50.0

    # weak enemy that dies to detonation
    enemy1 = MockBall(60, 50, "blue")
    enemy1.id = 2
    enemy1.hp = 10.0 # Will die

    # healthy enemy nearby that survives detonation
    enemy2 = MockBall(70, 50, "blue")
    enemy2.id = 3
    enemy2.hp = 100.0

    world.balls.extend([clone, enemy1, enemy2])

    action = Action(clone, world)
    # trigger detonation
    action.execute("idle", 0.1)

    assert not clone.alive
    assert not enemy1.alive
    assert enemy2.hp == 80.0

    # Test if cascade clone was spawned
    cascade_clones = [b for b in world.balls if getattr(b, "is_mimic_charging", False) and getattr(b, "mimic_cascade", False) and b.id != clone.id]

    assert len(cascade_clones) == 1
    cascade_clone = cascade_clones[0]
    assert cascade_clone.max_hp == 25.0
    assert cascade_clone.hp == 25.0

test_mimic_cascade()
print("Success")
