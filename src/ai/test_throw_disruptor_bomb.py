import pytest
import os
import sys

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from ai.action import Action

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards

class MockWorld:
    def __init__(self, arena, balls):
        self.arena = arena
        self.balls = balls
        self.entities = balls
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
        self.aura_disruption_timer = 0.0

def test_throw_disruptor_bomb_skill():
    arena = MockArena([])
    brawler = MockBall(1, 0, 0, "throw_disruptor_bomb", team="teamA")
    enemy = MockBall(2, 100, 0, "none", team="teamB")
    ally = MockBall(3, 100, 50, "none", team="teamA")

    world = MockWorld(arena, [brawler, enemy, ally])
    action = Action(brawler, world)

    action._use_skill()

    # Needs to spawn a thrown_disruptor_bomb hazard moving to enemy
    assert len(arena.hazards) == 1
    bomb = arena.hazards[0]
    assert bomb.kind == "thrown_disruptor_bomb"
    assert getattr(bomb, "duration", 0) > 0
    assert getattr(bomb, "team", None) == "teamA"

    # Advance time to explode
    bomb.duration = 0.001
    bomb.x = 100
    bomb.y = 0
    action.execute("idle", 0.016)

    # Bomb should be removed
    assert bomb not in arena.hazards

    # Enemy should have aura_disruption_timer applied (distance = 0)
    assert enemy.aura_disruption_timer >= 10.0

    # Ally should not have aura_disruption_timer applied (distance = 50, but team is same)
    assert ally.aura_disruption_timer == 0.0
