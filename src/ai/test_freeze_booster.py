import sys
import os
sys.path.insert(0, os.path.abspath('src'))
from ai.action import Action

class MockEntity:
    def __init__(self, id, x, y, kind=None):
        self.id = id
        self.x = x
        self.y = y
        self.kind = kind
        self.ball_type = "booster"
        self.duration = 3.0
        self.frozen_timer = 0.0

    def get(self, key, default=None):
        return getattr(self, key, default)

class MockBall:
    def __init__(self, team="team1"):
        self.id = 1
        self.team = team
        self.x = 0
        self.y = 0
        self.radius = 10
        self.stun_timer = 0
        self.speed = 2
        self.used_skill_count = 0
        self.alive = True
        self.ball_type = "warrior"
        self.base_speed = 10
        self.hp = 100
        self.stamina = 100

class MockWorld:
    def __init__(self):
        self.balls = []
        self.boosters = []
        self.entities = []
        self.arena = type('MockArena', (), {'hazards': []})()

    def get_nearby_entities(self, ball, radius):
        return {
            "enemies": [b for b in self.balls if b.team != ball.team],
            "allies": [],
            "boosters": self.boosters
        }

def test_collect_freeze_booster():
    ball = MockBall()
    enemy = MockBall(team="team2")
    enemy.id = 2
    enemy.x = 50
    enemy.y = 0

    enemy_far = MockBall(team="team2")
    enemy_far.id = 3
    enemy_far.x = 2000 # very far
    enemy_far.y = 0

    ally = MockBall(team="team1")
    ally.id = 4
    ally.x = 50
    ally.y = 0

    booster = MockEntity(2, 0, 0, kind="freeze_booster")

    hazard1 = MockEntity(3, 100, 100, kind="lava")

    world = MockWorld()
    world.balls = [ball, enemy, enemy_far, ally]
    world.entities = [ball, enemy, enemy_far, ally]
    world.boosters = [booster]
    world.arena.hazards = [booster, hazard1]

    action = Action(ball, world)
    action.execute("collect_booster", 1.0)

    # Check enemies in arena get stunned/frozen
    assert enemy.stun_timer == 3.0
    assert enemy_far.stun_timer == 3.0 # it should freeze ALL enemies
    # Check ally is not stunned
    assert ally.stun_timer == 0
    # Check hazards are frozen
    assert hazard1.frozen_timer == 3.0
    # Check booster is removed from hazards
    assert len(world.arena.hazards) == 1
    assert hazard1 in world.arena.hazards

if __name__ == "__main__":
    test_collect_freeze_booster()
    print("Test passed!")
