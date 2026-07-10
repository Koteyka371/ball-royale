import os
import sys
sys.path.insert(0, os.path.abspath('src'))
from ai.action import Action

class MockEntity:
    def __init__(self, id, x, y, kind=None):
        self.id = id
        self.x = x
        self.y = y
        self.kind = kind
        self.duration = 5.0
        self.radius = 15.0
        self.damage = 0.0

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self, arena, balls):
        self.arena = arena
        self.balls = balls
        self.entities = balls
        self.events = []

    def get_nearby_entities(self, ball, radius):
        return {
            "enemies": [b for b in self.balls if b.team != ball.team],
            "allies": []
        }

class MockBall:
    def __init__(self, id, x, y, skill, team=""):
        self.id = id
        self.x = x
        self.y = y
        self.skill = skill
        self.skill_timer = 0.0
        self.skill_cooldown = 4.0
        self.radius = 10.0
        self.alive = True
        self.ball_type = "brawler"
        self.team = team
        self.hp = 100.0

def test_disruption_bomb():
    arena = MockArena([])
    attacker = MockBall(1, 0, 0, "disruption_bomb", team="teamA")
    enemy1 = MockBall(2, 50, 0, "none", team="teamB")
    enemy2 = MockBall(3, 300, 0, "none", team="teamB")

    world = MockWorld(arena, [attacker, enemy1, enemy2])
    action = Action(attacker, world)

    action._use_skill()

    assert len(arena.hazards) == 1
    bomb = arena.hazards[0]
    assert bomb.kind == "disruption_bomb"
    assert bomb.owner_id == attacker.id

    # advance to detonate
    bomb.duration = 0.01
    action.execute("idle", 0.05)

    assert len(arena.hazards) == 0

    # check timers
    assert getattr(enemy1, "aura_disruption_timer", 0.0) == 10.0
    assert getattr(enemy2, "aura_disruption_timer", 0.0) == 0.0 # too far
    assert getattr(attacker, "aura_disruption_timer", 0.0) == 0.0 # friendly fire disabled

    assert len(world.events) > 0
    assert world.events[0]['type'] == 'visual_effect'

if __name__ == "__main__":
    test_disruption_bomb()
    print("Test passed!")
