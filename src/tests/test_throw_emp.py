import sys
import os
sys.path.insert(0, os.path.abspath('src'))
from ai.action import Action

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards

class MockWorld:
    def __init__(self, arena, balls):
        self.arena = arena
        self.balls = balls
        self.events = []

    def get_nearby_entities(self, entity, radius):
        return {"enemies": [b for b in self.balls if b != entity and b.team != entity.team]}

class MockBall:
    def __init__(self, id, x, y, skill, team=""):
        self.id = id
        self.x = x
        self.y = y
        self.skill = skill
        self.skill_timer = 0.0
        self.skill_cooldown = 4.0
        self.silence_timer = 0.0
        self.radius = 10.0
        self.alive = True
        self.ball_type = "brawler" if id == 1 else "enemy"
        self.team = team
        self.hp = 100.0
        self.vx = 0.0
        self.vy = 0.0
        self.shield = 50.0
        self.speed = 10.0

class MockHazard:
    def __init__(self, kind, x, y):
        self.kind = kind
        self.x = x
        self.y = y
        self.emp_disabled_timer = 0.0

def test_throw_emp_skill():
    arena = MockArena([MockHazard("laser_beam", 100, 0)])
    brawler = MockBall(1, 0, 0, "throw_emp", team="teamA")
    enemy = MockBall(2, 100, 0, "none", team="teamB")
    ally = MockBall(3, 100, 50, "none", team="teamA")

    world = MockWorld(arena, [brawler, enemy, ally])
    action = Action(brawler, world)

    action._use_skill()

    # Needs to spawn a thrown_emp hazard moving to enemy
    assert len(arena.hazards) == 2
    emp = arena.hazards[1]
    assert emp.kind == "thrown_emp"
    assert getattr(emp, "duration", 0) > 0
    assert getattr(emp, "team", None) == "teamA"

    # Advance time to explode
    emp.duration = 0.001
    emp.x = 100
    emp.y = 0
    action.execute("idle", 0.016)

    # EMP should be removed
    assert emp not in arena.hazards

    # Enemy should have speed 0 and shield 0
    assert enemy.speed == 0.0
    assert enemy.shield == 0.0
    assert enemy.skill_timer >= 3.0

    # Ally should not be affected
    assert ally.speed == 10.0
    assert ally.shield == 50.0

    # Laser should be disabled
    assert arena.hazards[0].emp_disabled_timer >= 5.0
