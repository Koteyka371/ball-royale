import pytest
from ai.action import Action

class MockBall:
    def __init__(self, id, x, y, team, radius=10.0, base_speed=100.0, damage_multiplier=1.0):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.radius = radius
        self.base_speed = base_speed
        self.damage_multiplier = damage_multiplier
        self.speed = base_speed
        self.hp = 100.0

class MockHazard:
    def __init__(self, id, x, y, radius, kind, owner_id):
        self.id = id
        self.x = x
        self.y = y
        self.radius = radius
        self.kind = kind
        self.owner_id = owner_id
        self.duration = 10.0

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []

def test_empowerment_matrix():
    world = MockWorld()

    # Owner team 1
    owner = MockBall(1, 0, 0, "team1")
    world.balls.append(owner)

    # Ally team 1
    ally = MockBall(2, 0, 0, "team1")
    world.balls.append(ally)

    # Enemy team 2
    enemy = MockBall(3, 0, 0, "team2")
    world.balls.append(enemy)

    # Hazard owned by team 1
    matrix = MockHazard(1, 0, 0, 50.0, "empowerment_matrix", 1)
    world.arena.hazards.append(matrix)

    # Test Ally
    action_ally = Action(ally, world)
    action_ally.execute("idle", 1.0)

    assert ally.speed == 150.0
    assert ally.damage_multiplier == 1.5
    assert hasattr(ally, "empowerment_boost_timer")
    assert ally.empowerment_boost_timer == 0.5

    # Test Enemy
    action_enemy = Action(enemy, world)
    action_enemy.execute("idle", 1.0)

    assert enemy.speed == 50.0
    assert enemy.damage_multiplier == 1.0 # Should not change
