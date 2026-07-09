import pytest
from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []
        self.boundary_states = {}
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self, balls=None):
        self.balls = balls if balls is not None else []
        self.arena = MockArena()
        self.damage_dealt = []

    def get_nearby_entities(self, entity, radius):
        return []

    def _deal_damage(self, attacker, target):
        self.damage_dealt.append((attacker, target))
        if hasattr(target, "hp"):
            target.hp -= getattr(attacker, "damage", 10.0)

class MockHazard:
    def __init__(self, kind):
        self.kind = kind
        self.x = 100
        self.y = 100
        self.radius = 15.0
        self.duration = 5.0

class MockBall:
    def __init__(self, id, team):
        self.id = id
        self.team = team
        self.x = 100
        self.y = 100
        self.radius = 10.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.damage = 20.0
        self.vx = 0.0
        self.vy = 0.0

def test_friendly_fire_reflect_hazard():
    ball = MockBall(1, "A")
    world = MockWorld([ball])
    action = Action(ball, world)

    # Add trap
    trap = MockHazard("friendly_fire_reflect_trap")
    world.arena.hazards.append(trap)

    action.execute("idle", 0.1)

    assert getattr(ball, "friendly_fire_reflect_active", False)
    assert getattr(ball, "friendly_fire_reflect_timer", 0.0) == 5.0
    assert trap not in world.arena.hazards

    # Now simulate a friendly attack
    ally_attacker = MockBall(2, "A")
    ally_attacker.damage = 30.0

    # Attacker tries to attack ball
    action._attempt_damage(ally_attacker, ball)

    # Since ball has reflect, ally should take damage instead
    assert ball.hp == 100.0
    assert ally_attacker.hp == 70.0  # (100 - 30)

def test_enemy_damage_not_reflected():
    ball = MockBall(1, "A")
    ball.friendly_fire_reflect_active = True
    world = MockWorld([ball])
    action = Action(ball, world)

    enemy_attacker = MockBall(3, "B")
    enemy_attacker.damage = 25.0

    action._attempt_damage(enemy_attacker, ball)

    # Enemy damage is not reflected
    assert ball.hp == 75.0
    assert enemy_attacker.hp == 100.0
