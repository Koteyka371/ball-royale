import sys
import os
sys.path.insert(0, os.path.abspath('src'))
from ai.action import Action
import math

class MockEntity:
    def __init__(self, id, x, y, kind=None):
        self.id = id
        self.x = x
        self.y = y
        self.kind = kind
        self.ball_type = "booster"
        self.duration = 5.0

    def get(self, key, default=None):
        return getattr(self, key, default)

class MockBall:
    def __init__(self, team="team1"):
        self.id = 1
        self.team = team
        self.x = 0
        self.y = 0
        self.radius = 10
        self.silence_timer = 0
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
        self.arena = type('MockArena', (), {'hazards': []})()

    def get_nearby_entities(self, ball, radius):
        return {
            "enemies": [b for b in self.balls if b.team != ball.team],
            "allies": [],
            "boosters": self.boosters
        }

def test_collect_silence_booster():
    ball = MockBall()
    enemy = MockBall(team="team2")
    enemy.id = 2
    enemy.x = 50
    enemy.y = 0

    enemy_far = MockBall(team="team2")
    enemy_far.id = 3
    enemy_far.x = 200 # out of 150 range
    enemy_far.y = 0

    ally = MockBall(team="team1")
    ally.id = 4
    ally.x = 50
    ally.y = 0

    booster = MockEntity(2, 0, 0, kind="silence_booster")

    world = MockWorld()
    world.balls = [ball, enemy, enemy_far, ally]
    world.boosters = [booster]
    world.arena.hazards = [booster]

    action = Action(ball, world)
    action.execute("collect_booster", 1.0)

    # Check enemy in range gets silenced
    assert enemy.silence_timer == 5.0
    # Check enemy out of range is not silenced
    assert enemy_far.silence_timer == 0
    # Check ally is not silenced
    assert ally.silence_timer == 0
    # Check booster is removed from hazards
    assert len(world.arena.hazards) == 0
