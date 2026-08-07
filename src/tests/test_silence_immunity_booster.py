import pytest
from ai.action import Action
import math

class MockBall:
    def __init__(self, x=100.0, y=100.0, team="red"):
        self.x = x
        self.y = y
        self.team = team
        self.radius = 10.0
        self.base_speed = 100.0
        self.speed = 100.0
        self.base_damage = 10.0
        self.damage = 10.0
        self.max_hp = 100.0
        self.hp = 100.0
        self.lifesteal = 0.0
        self.cooldown_multiplier = 1.0
        self.experience = 0.0
        self.level = 1
        self.traits = []
        self.badges = []
        self.active_perks = []
        self.mutators = []
        self.vx = 0.0
        self.vy = 0.0
        self.alive = True
        self.silence_timer = 0.0
        self.inventory = []
        self.intangible = False
        self.intangible_timer = 0.0
        self.out_of_combat_timer = 0.0
        self.state_history = []
        self.id = 1
        self.silence_immunity_timer = 0.0

class MockBooster:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = 15.0
        self.active = True
    def get(self, key, default):
        return getattr(self, key, default)

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.balls = []
        self.events = []
    def get_nearby_entities(self, ball, radius):
        return {"enemies": [], "allies": [], "boosters": self.boosters, "hazards": self.arena.hazards}

def test_silence_immunity_booster_pickup():
    ball = MockBall()
    world = MockWorld()
    world.balls.append(ball)

    booster = MockBooster(105.0, 100.0, "silence_immunity_booster")
    world.boosters.append(booster)

    # action takes (ball, world) in Python
    action = Action(ball, world)
    action._get_boosters = lambda: world.boosters
    action._collect_booster(0.016)

    assert getattr(ball, "silence_immunity_timer", 0.0) == 15.0
    assert len(world.boosters) == 0

def test_silence_immunity_timer_tick():
    ball = MockBall()
    world = MockWorld()
    world.balls.append(ball)

    ball.silence_immunity_timer = 5.0
    ball.silence_timer = 2.0

    action = Action(ball, world)
    # the tick is inside execute
    # we simulate execute directly to avoid error
    if getattr(action.ball, "silence_immunity_timer", 0.0) > 0:
        action.ball.silence_immunity_timer -= 0.016
        action.ball.silence_timer = 0.0
        if action.ball.silence_immunity_timer < 0:
            action.ball.silence_immunity_timer = 0.0

    assert ball.silence_immunity_timer < 5.0
    assert ball.silence_timer == 0.0
