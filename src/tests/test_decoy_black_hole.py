import pytest
import sys
import os
sys.path.append(os.path.abspath('src'))
from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []
        self.projectiles = []
        self.width = 1000
        self.height = 1000
    def clamp_position(self, x, y, r):
        return x, y, False

class MockWorld:
    def __init__(self, arena, balls=None):
        self.arena = arena
        self.balls = balls if balls else []
        self.events = []
        self.tick = 0
    def add_event(self, event_type, data):
        pass
    def get_nearby_entities(self, b, r):
        return {'boosters': [], 'hazards': [], 'enemies': [], 'allies': [], 'items': []}

class MockBall:
    def __init__(self, id, x, y, team="team_a"):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.alive = True
        self.hp = 100.0
        self.max_hp = 100.0
        self.vx = 0
        self.vy = 0
        self.speed = 0
        self.ball_type = "base"
        self.traits = []

class MockProjectile:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.active = True

def test_black_hole_decoy_pull():
    arena = MockArena()

    # Black hole decoy at center
    decoy = MockBall(id=1, x=500, y=500, team="team_a")
    decoy.is_decoy = True
    decoy.decoy_type = "black_hole"
    decoy.decoy_timer = 5.0
    decoy.owner_id = 999

    # Enemy at 600, 500 (distance 100, within 250 pull radius)
    enemy = MockBall(id=2, x=600, y=500, team="team_b")

    # Projectile at 500, 600 (distance 100, within 250 pull radius)
    projectile = MockProjectile(x=500, y=600)
    arena.projectiles.append(projectile)

    world = MockWorld(arena, [decoy, enemy])

    # Tick 1: Action should process the decoy logic and pull the enemy and projectile
    action = Action(decoy, world)
    action.execute("idle", 0.1)

    # Initial positions were 600 and 600
    # Pull logic should reduce distance
    assert enemy.x < 600, f"Enemy should be pulled towards 500, but is at {enemy.x}"
    assert enemy.y == 500
    assert projectile.x == 500
    assert projectile.y < 600, f"Projectile should be pulled towards 500, but is at {projectile.y}"
