import sys
import os
sys.path.insert(0, os.path.abspath('src'))
from ai.action import Action
from ai.perception import Perception

class MockEntity:
    def __init__(self, x=0, y=0, kind="ghost_mode_booster", radius=15.0, hp=100.0, alive=True, damage=0.0):
        self.damage = damage
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = radius
        self.hp = hp
        self.alive = alive
        self.id = 999
        self.team = "test_team"
        self.ball_type = "booster"

    def get(self, key, default=None):
        return getattr(self, key, default)

    def has_method(self, name):
        return False

class MockBall(MockEntity):
    def __init__(self, x=0, y=0, radius=10.0, hp=100.0, alive=True):
        super().__init__(x, y, "ball", radius, hp, alive)
        self.speed = 2.0
        self.base_speed = 10.0
        self.stamina = 100.0
        self.max_hp = 100.0
        self.perception_radius = 250.0
        self.ball_type = "basic"
        self.is_decoy = False
        self.is_illusion = False

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.balls = []
        self.next_id = 1000

    def get_nearby_entities(self, ball, radius):
        return {
            "enemies": [b for b in self.balls if b.team != ball.team],
            "allies": [b for b in self.balls if b.team == ball.team and b != ball],
            "boosters": self.boosters,
            "traps": []
        }

def test_ghost_mode_booster():
    ball = MockBall(x=100, y=100)
    ball.id = 1
    ball.team = "blue"

    ally = MockBall(x=120, y=100)
    ally.id = 2
    ally.team = "blue"

    far_ally = MockBall(x=500, y=500)
    far_ally.id = 4
    far_ally.team = "blue"

    enemy = MockBall(x=200, y=100)
    enemy.id = 3
    enemy.team = "red"
    enemy.is_turret = True

    world = MockWorld()
    world.balls = [ball, ally, far_ally, enemy]

    ghost_booster = MockEntity(x=100, y=100, kind="ghost_mode_booster")
    world.boosters = [ghost_booster]
    world.arena.hazards = [ghost_booster]

    action = Action(ball, world)
    action.execute("collect_booster", 1.0)

    assert getattr(ball, "ghost_mode_timer", 0) > 0
    assert getattr(ally, "ghost_mode_timer", 0) > 0
    assert getattr(far_ally, "ghost_mode_timer", 0) == 0 # Too far

    assert getattr(ball, "intangible", False)
    assert getattr(ally, "intangible", False)
    assert not getattr(far_ally, "intangible", False)

    # Test perception distance
    enemy_action = Action(enemy, world)
    targets = enemy_action._get_enemies()
    assert 1 not in [t.id for t in targets]
    assert 2 not in [t.id for t in targets]

    # Move close
    ball.x = 210
    ball.y = 100
    targets = enemy_action._get_enemies()
    assert 1 in [t.id for t in targets]
