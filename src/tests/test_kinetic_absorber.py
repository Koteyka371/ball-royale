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

class MockEnemy:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.alive = True
        self.team = "team_b"
        self.vx = 0.0
        self.vy = 0.0

class MockHazard:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0

def test_kinetic_absorber():
    world = MockWorld()
    ball = MockBall(1, 100.0, 100.0, "kinetic_absorber")
    enemy = MockEnemy(2, 110.0, 100.0) # Right next to ball
    hazard = MockHazard(3, 90.0, 100.0)
    world.arena.hazards.append(hazard)

    action = Action(ball, world)

    # Mocking _get_enemies to return our enemy
    action._get_enemies = lambda: [enemy]

    # 1. Trigger skill activation by incrementing skill_timer over prev_skill_timer
    ball.skill_timer = 10.0
    action._update_skill_timer(0.0)

    assert ball.has_kinetic_absorber is True
    assert ball.kinetic_energy_pool == 0.0
    assert ball.kinetic_absorber_duration == 3.0
    assert any(e['type'] == 'visual_effect' and e['data']['type'] == 'kinetic_absorber_activated' for e in world.events)

    # 2. Simulate taking damage while active
    attacker = type('Attacker', (), {'damage': 50.0, 'vx': 100.0, 'vy': 0.0, 'mass': 1.0, 'in_mirror_dimension': False})()
    ball.in_mirror_dimension = False
    action._attempt_damage(attacker, ball)

    # 50 damage + 100 speed * 1 mass * 0.01 = 51 energy
    assert ball.kinetic_energy_pool == 51.0

    # 3. Simulate time expiring
    action._update_skill_timer(3.0)

    assert ball.has_kinetic_absorber is False

    # Verify shockwave pushed enemy and hazard
    # shockwave force: 500 + 51 * 2 = 602
    assert enemy.vx > 0.0 # Enemy was at 110, ball at 100, push is positive X
    assert hazard.vx < 0.0 # Hazard was at 90, ball at 100, push is negative X
