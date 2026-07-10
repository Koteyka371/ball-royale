import pytest
from ai.action import Action

class MockWorld:
    def __init__(self):
        self.events = []
        self.balls = []
        self.next_id = 10000

    def add_event(self, event_type, data):
        self.events.append({"type": event_type, "data": data})

class MockBall:
    def __init__(self):
        self.alive = True
        self.level = 9
        self.experience = 900
        self.ball_type = "warrior"
        self.id = 1
        self.x = 0
        self.y = 0
        self.hp = 100
        self.max_hp = 100
        self.damage = 10
        self.speed = 100
        self.team = "player"

def test_world_boss_spawn_at_max_level():
    world = MockWorld()
    ball = MockBall()
    world.balls.append(ball)

    action = Action(ball, world)

    import random
    original_random = random.random

    # Force the 30% chance to happen by returning 0.1
    random.random = lambda: 0.1

    try:
        # Give enough xp to reach level 10
        action._award_xp(ball, 100, world)
    finally:
        random.random = original_random

    assert ball.level == 10
    assert len(world.balls) == 2, "Boss should have been spawned"

    boss = world.balls[1]
    assert getattr(boss, "is_world_boss", False) is True
    assert getattr(boss, "team", "") == "corrupted_bosses"
    assert getattr(boss, "max_hp", 0) == 1000
    assert getattr(boss, "damage", 0) == 30
    assert getattr(boss, "speed", 0) == 150
    assert getattr(boss, "ball_type", "") == "warrior"

    events = [e for e in world.events if e["type"] == "world_boss_spawned"]
    assert len(events) == 1
    assert events[0]["data"]["boss_type"] == "warrior"

def test_world_boss_spawn_failure_chance():
    world = MockWorld()
    ball = MockBall()
    world.balls.append(ball)

    action = Action(ball, world)

    import random
    original_random = random.random

    # Fail the 30% chance by returning 0.5
    random.random = lambda: 0.5

    try:
        # Give enough xp to reach level 10
        action._award_xp(ball, 100, world)
    finally:
        random.random = original_random

    assert ball.level == 10
    assert len(world.balls) == 1, "Boss should NOT have been spawned"
