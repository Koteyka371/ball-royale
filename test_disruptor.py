import sys
import os

# Add src to the path
sys.path.insert(0, os.path.abspath('src'))

from ai.action import Action

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards

class MockWorld:
    def __init__(self, arena, balls):
        self.arena = arena
        self.balls = balls
        self.entities = balls

    def get_nearby_entities(self, entity, radius):
        return {"enemies": [b for b in self.balls if b != entity]}

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
    assert arena.hazards[0].kind == "disruption_bomb"

test_disruption_bomb()
print("test finished")
