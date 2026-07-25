import sys
sys.path.append('src')
import pytest
from ai.action import Action
class MockArena:
    def __init__(self):
        self.hazards = []
class MockWorld:
    def __init__(self):
        self.events = []
        self.arena = MockArena()
class MockBall:
    def __init__(self, id, x, y, skill):
        self.id = id
        self.x = x
        self.y = y
        self.skill = skill
        self.skill_timer = 0.0
        self._prev_skill_timer = 0.0
        self.alive = True
        self.team = "team_a"
        self.SKILL_COOLDOWN = 10.0
        self.vx = 0.0
        self.vy = 0.0
        self.mass = 1.0
        self.radius = 10.0
class MockEnemy:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.alive = True
        self.team = "team_b"
        self.vx = 0.0
        self.vy = 0.0
        self.mass = 1.0
        self.radius = 10.0
def test_kinetic_absorber_knockback_absorption():
    world = MockWorld()
    ball = MockBall(1, 100.0, 100.0, "kinetic_absorber")
    # Place enemy so that they intersect heavily, producing a high overlap (dx=-10, dy=0, dist=10, min_dist=20, overlap=10)
    enemy = MockEnemy(2, 90.0, 100.0)
    action = Action(ball, world)

    # 1. Trigger skill activation by incrementing skill_timer over prev_skill_timer
    ball.skill_timer = 10.0
    action._update_skill_timer(0.0)

    assert ball.has_kinetic_absorber is True

    action.world.get_nearby_entities = lambda b, r: [enemy]

    action._resolve_collisions()

    # We expect speed boost timer and kinetic energy pool to be increased
    assert getattr(ball, "kinetic_absorbed_energy", 0) > 0
    assert getattr(ball, "speed_boost_timer", 0) > 0
    assert getattr(ball, "supercharge_timer", 0) > 0
