import pytest
from ai.action import Action

class MockWorld:
    def __init__(self):
        self.events = []
        self.arena = MockArena()

    def _deal_damage(self, attacker, target):
        target.hp -= attacker.damage
        if target.hp > target.max_hp:
            target.hp = target.max_hp

    def get_nearby_entities(self, ball, radius):
        allies = [b for b in self.balls if b.team == ball.team and b != ball]
        enemies = [b for b in self.balls if b.team != ball.team]
        return {"allies": allies, "enemies": enemies, "boosters": []}

class MockArena:
    def __init__(self):
        self.hazards = []

class MockBall:
    def __init__(self, ball_id, x, y, team, hp, max_hp, is_turret=False, owner_id=None):
        self.id = ball_id
        self.x = x
        self.y = y
        self.team = team
        self.hp = hp
        self.max_hp = max_hp
        self.alive = True
        self.is_turret = is_turret
        self.owner_id = owner_id
        self.speed = 100.0
        self.attack_timer = 0.0
        self.radius = 10.0
        self.attack_range = 250.0

def test_turret_heals_ally():
    world = MockWorld()

    owner = MockBall(1, 0, 0, "team1", 100, 100)

    turret = MockBall(2, 10, 10, "team1", 50, 50, is_turret=True, owner_id=1)
    turret.damage = -10 # Negative damage = healing

    ally = MockBall(3, 20, 20, "team1", 50, 100)

    world.balls = [owner, turret, ally]

    action = Action(turret, world)
    action._chase(0.1)

    # Check if ally was healed
    assert ally.hp > 50
    assert ally.hp == 60
