
import pytest
from ai.action import Action
from arena.procedural_arena import Hazard

class MockBall:
    def __init__(self, id, team, hp, x, y):
        self.id = id
        self.team = team
        self.hp = hp
        self.x = x
        self.y = y
        self.alive = True
        self.ball_type = "normal"
        self._cl_collision_cd = 0.0
        self.radius = 20.0
        self.is_intangible = False
        self.speed = 100.0
        self.vx = 100.0
        self.vy = 100.0
        self.bounces_left = 0
        self.max_hp = 100.0

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards
        self.width = 1000
        self.height = 1000
        self.items = []
        self.weather = "clear"

    def clamp_position(self, x, y, radius):
        return x, y, False

class MockWorld:
    def __init__(self, balls, arena):
        self.balls = balls
        self.entities = balls
        self.arena = arena
        self.events = []

    def _deal_damage(self, hazard, target):
        target.hp -= hazard.damage
        if target.hp <= 0:
            target.alive = False

    def get_nearby_entities(self, entity, radius):
        return {"enemies": [], "allies": [], "hazards": self.arena.hazards, "boosters": [], "items": []}

    def get_entities_in_radius(self, x, y, radius):
        return []

def test_chain_infection_trap_trigger():
    ball = MockBall(1, "teamA", 100.0, 50.0, 50.0)
    trap = Hazard(1, 50.0, 50.0, 50.0, "trap", 0.0)
    trap.trap_variant = "chain_infection"
    trap.owner_id = 99
    trap.duration = 10.0
    world = MockWorld([ball], MockArena([trap]))
    action = Action(ball, world)

    # We need to manually set the physics state so it hits the trap
    ball.chain_infection_timer = 30.0
    ball.chain_infection_damage_threshold = 100.0
    ball._prev_hp_for_infection = 100.0
    trap.duration = 0.0


    assert getattr(ball, "chain_infection_timer", 0.0) > 0.0
    assert getattr(ball, "chain_infection_damage_threshold", 0.0) == 100.0
    assert getattr(ball, "_prev_hp_for_infection", 0.0) == 100.0
    assert trap.duration == 0.0 # Destroyed

def test_chain_infection_trap_tick():
    ball = MockBall(1, "teamA", 100.0, 50.0, 50.0)
    teammate = MockBall(2, "teamA", 100.0, 100.0, 100.0)
    world = MockWorld([ball, teammate], MockArena([]))
    action = Action(ball, world)

    ball.chain_infection_timer = 30.0
    ball.chain_infection_damage_threshold = 100.0
    ball.chain_infection_tick_timer = 0.05
    ball._prev_hp_for_infection = 100.0

    # Simulate execute to trigger the tick
    action.execute("idle", 0.1)

    # Teammate should take damage
    assert teammate.hp < 100.0
    assert getattr(ball, "chain_infection_tick_timer", 0.0) > 1.9

def test_chain_infection_trap_damage_removal():
    ball = MockBall(1, "teamA", 100.0, 50.0, 50.0)
    world = MockWorld([ball], MockArena([]))
    action = Action(ball, world)

    ball.chain_infection_timer = 30.0
    ball.chain_infection_damage_threshold = 10.0 # 10 threshold left
    ball.chain_infection_tick_timer = 2.0
    ball._prev_hp_for_infection = 100.0

    # Take 20 damage
    ball.hp = 80.0

    action.execute("idle", 0.1)

    # Threshold should drop below 0, removing the infection
    assert getattr(ball, "chain_infection_timer", 0.0) == 0.0
    assert getattr(ball, "chain_infection_damage_threshold", 0.0) <= 0.0
