import pytest
from ai.action import Action

class MockWorld:
    def __init__(self):
        self.next_id = 1000
        self.balls = []
        self.arena = type('obj', (object,), {'hazards': [], 'width': 1000, 'height': 1000})()
    def get_nearby_entities(self, ball, radius):
        return {"boosters": [], "hazards": []}
    def _deal_damage(self, attacker, target, dmg=None):
        pass

class MockBall:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.radius = 15.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.id = 1
        self.team = "team1"
        self.ball_type = "easy"
        self.speed = 2.5
        self.base_speed = 2.5
        self.attack_timer = 0.0

def test_frost_minion_targets_closest():
    world = MockWorld()
    world.next_id = 1000

    fm = MockBall()
    fm.ball_type = "frost_minion"
    fm.hp = 15
    fm.team = "undead"
    fm.speed = 2.5
    fm.id = 1
    fm.x = 500
    fm.y = 500
    fm.attack_timer = 0.0

    enemy_close = MockBall()
    enemy_close.team = "hero"
    enemy_close.hp = 100
    enemy_close.id = 2
    enemy_close.x = 600
    enemy_close.y = 500

    enemy_far = MockBall()
    enemy_far.team = "hero"
    enemy_far.hp = 100
    enemy_far.id = 3
    enemy_far.x = 900
    enemy_far.y = 500

    world.balls = [fm, enemy_close, enemy_far]

    action = Action(fm, world)
    action._get_enemies = lambda: [enemy_close, enemy_far]

    # Force attack timer to be ready and let it fire
    action.execute("idle", 0.016)

    assert len(world.arena.hazards) == 1
    bolt = world.arena.hazards[0]

    # Frost bolt should go towards the closest enemy
    # dx = 100, dy = 0, so vx > 0 and vy == 0
    assert bolt.vx > 0
    assert bolt.vy == 0
