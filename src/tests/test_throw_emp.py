import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []

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
        self.ball_type = "brawler"
        self.team = team
        self.hp = 100.0
        self.vx = 0.0
        self.vy = 0.0
        self.speed = 2.0
        self.base_speed = 2.0
        self.shield_timer = 5.0
        self.emp_disabled_timer = 0.0

def test_throw_emp_skill():
    arena = MockArena()
    brawler = MockBall(1, 0, 0, "throw_emp", team="teamA")
    enemy = MockBall(2, 100, 0, "none", team="teamB")

    world = MockWorld(arena, [brawler, enemy])
    action = Action(brawler, world)

    action._use_skill()

    assert len(arena.hazards) == 1
    bomb = arena.hazards[0]
    assert bomb.kind == "thrown_emp"

    # advance to explode
    bomb.duration = 0.001
    bomb.x = 100
    bomb.y = 0

    # enemy has active shield
    enemy.shield_timer = 10.0
    enemy.speed = 100.0
    enemy.shield = 50.0

    # trap near enemy
    class MockTrap:
        def __init__(self):
            self.x = 110
            self.y = 0
            self.emp_disabled_timer = 0.0
            self.active = True
    trap = MockTrap()
    arena.hazards.append(trap)

    action.execute("idle", 0.016)

    # exploded
    assert bomb not in arena.hazards

    # Check effects: speed to zero, active shield turned off
    assert enemy.speed == 0.0
    assert getattr(enemy, "shield_timer", 0.0) == 0.0
    assert getattr(enemy, "shield", 0.0) == 0.0

    # Trap disabled
    assert trap.emp_disabled_timer > 0.0
