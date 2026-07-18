import pytest
from ai.action import Action

class MockBall:
    def __init__(self, id, x, y, team):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.ball_type = "brawler"
        self.radius = 10.0
        self.speed = 100.0
        self.vx = 0.0
        self.vy = 0.0
        self.base_speed = 100.0
        self.team_tether_timer = 0.0
        self.team_tether_target = None
        self.disoriented_timer = 0.0
        self.is_confused = False
        self.in_mirror_dimension = False
        self.intangible = False
        self.intangible_timer = 0.0

class MockHazard:
    def __init__(self, kind, x, y):
        self.kind = kind
        self.x = x
        self.y = y
        self.id = 999
        self.radius = 10.0

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards
        self.width = 1000
        self.height = 1000

    def clamp_position(self, x, y, r):
        return (x, y, False)

    def is_valid_position(self, x, y, radius):
        return True

class MockWorld:
    def __init__(self, balls, boosters):
        self.balls = balls
        self.boosters = boosters
        self.arena = MockArena(boosters.copy())
        self.events = []

    def get_nearby_entities(self, ball, radius):
        enemies = [b for b in self.balls if b.team != ball.team and b.alive]
        allies = [b for b in self.balls if b.team == ball.team and b != ball and b.alive]
        return {
            "enemies": enemies,
            "allies": allies,
            "boosters": self.boosters,
            "hazards": self.arena.hazards
        }

def test_team_tether_booster():
    collector = MockBall(1, 100, 100, "team1")
    ally = MockBall(2, 200, 200, "team1")
    enemy = MockBall(3, 100, 110, "team2")

    booster = MockHazard("team_tether_booster", 102, 102)
    world = MockWorld([collector, ally, enemy], [booster])

    action = Action(collector, world)

    # Avoid interruption by flee logic due to nearby enemies
    enemy.y = 160

    action._get_boosters = lambda: [booster]
    action._get_enemies = lambda: [enemy]
    action._get_allies = lambda: [ally]

    # 1. Collect booster
    action._collect_booster(1.0)

    # Check if tether is applied to enemy towards ally
    assert enemy.team_tether_timer == 5.0
    assert enemy.team_tether_target == ally

    # Booster should be removed
    assert booster not in world.boosters
    assert booster not in world.arena.hazards

    # 2. Tick enemy to simulate pull and damage
    enemy_action = Action(enemy, world)

    initial_enemy_x = enemy.x
    initial_enemy_y = enemy.y
    initial_enemy_hp = enemy.hp

    # Ensure team_tether_timer > 0 gets processed
    # we do execute("idle") but idle itself moves the ball depending on its type and target.
    # To prevent idle movement from moving it AWAY from ally before tether pulls it,
    # we can zero out idle movement by mocking _idle
    original_idle = enemy_action._idle
    def fake_idle(delta): pass
    enemy_action._idle = fake_idle

    enemy_action.execute("idle", 0.1)

    # Enemy should be pulled towards ally (200, 200)
    assert enemy.x > initial_enemy_x
    assert enemy.y > initial_enemy_y

    # Enemy should take damage
    assert enemy.hp < initial_enemy_hp

    # Timer should decrement
    assert enemy.team_tether_timer < 5.0
