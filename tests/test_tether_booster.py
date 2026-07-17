import pytest
from ai.action import Action

class MockBall:
    def __init__(self, id, team, x, y):
        self.id = id
        self.team = team
        self.x = x
        self.y = y
        self.hp = 100.0
        self.alive = True
        self.radius = 10.0
        self.speed = 2.0
        self.base_speed = 2.0
        self.stamina = 100.0
        self.max_stamina = 100.0
        self.ball_type = "default"

class MockBooster:
    def __init__(self, kind, x, y):
        self.kind = kind
        self.x = x
        self.y = y
        self.active = True

class MockWorld:
    def __init__(self):
        self.balls = []
        self.boosters = []
        self.events = []
        self.arena = type('MockArena', (), {'hazards': [], 'width': 1000, 'height': 1000, 'safe_zone_center': (500, 500), 'safe_zone_radius': 500})()

    def get_nearby_entities(self, ball, radius):
        return []

def test_tether_booster_pickup():
    world = MockWorld()
    player = MockBall(1, 1, 100, 100)
    ally = MockBall(2, 1, 120, 100)
    enemy = MockBall(3, 2, 200, 100)
    booster = MockBooster("tether_booster", 102, 100)

    world.balls = [player, ally, enemy]
    world.boosters = [booster]

    action = Action(player, world)
    action._get_boosters = lambda: world.boosters
    action._get_enemies = lambda: [b for b in world.balls if b.team != player.team]
    action._get_allies = lambda: [b for b in world.balls if b.team == player.team and b != player]

    action._collect_booster(0.1)

    # Verify booster collected
    assert len(world.boosters) == 0

    # Verify enemy is tethered to ally
    assert getattr(enemy, "tether_booster_timer", 0) > 0
    assert getattr(enemy, "tether_booster_anchor", None) == ally

def test_tether_booster_effect():
    world = MockWorld()
    enemy = MockBall(1, 2, 200, 100)
    ally = MockBall(2, 1, 100, 100)

    enemy.tether_booster_timer = 5.0
    enemy.tether_booster_anchor = ally

    world.balls = [enemy, ally]

    action = Action(enemy, world)

    # Initial distance is 100 (dist_sq 10000)
    initial_hp = enemy.hp
    initial_x = enemy.x

    action.execute("flee", 0.1)

    # Timer should decrease
    assert enemy.tether_booster_timer < 5.0

    # Should take damage
    assert enemy.hp < initial_hp

    # Should be pulled towards ally (x should decrease)
    # The pull strength is 200 * delta = 20, so x should be around 180 (minus whatever flee might have done, but pull is strong)
    assert enemy.x < initial_x
