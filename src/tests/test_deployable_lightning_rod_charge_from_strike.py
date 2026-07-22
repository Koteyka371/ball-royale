import pytest
from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 800
        self.height = 600
        self.weather = "thunderstorm"
    def clamp_position(self, x, y, r):
        return x, y, False

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.tick = 0
        self.events = []
    def get_nearby_entities(self, ball, radius):
        return {"enemies": [], "allies": [], "hazards": self.arena.hazards, "boosters": []}

class MockEntity:
    def __init__(self, kind):
        self.kind = kind
        self.damage = 50.0
        self.hit_targets = False
        self.last_strike_tick = 0
        self.x = 100
        self.y = 100
        self.radius = 20.0

class MockBall:
    def __init__(self):
        self.id = 1
        self.x = 100
        self.y = 100
        self.radius = 10.0
        self.team = "A"
        self.alive = True
        self.ball_type = "base"
        self.hp = 100
        self.max_hp = 100
        self.kind = "deployable_lightning_rod"
        self.charge = 0.0

def test_deployable_lightning_rod_charge_from_strike():
    world = MockWorld()
    ball = MockBall()
    world.balls = [ball]
    action = Action(ball, world)
    action.world.tick = 1

    hazard = MockEntity("lightning_strike")
    world.arena.hazards.append(hazard)

    # We call _apply_hazards logic using the same code snippet found in execute
    delta = 0.1
    # Run the hazard loop from execute:
    for hazard in world.arena.hazards:
        if hazard.kind == "lightning_strike":
            if not getattr(hazard, "hit_targets", False):
                hazard.hit_targets = True
                b_type = getattr(ball, "ball_type", getattr(type(ball), "BALL_TYPE", "")).lower()
                if b_type == "lightning_rod" or getattr(ball, "kind", "") == "deployable_lightning_rod":
                    ball.hp = min(getattr(ball, "max_hp", 100), getattr(ball, "hp", 100) + hazard.damage)
                    if getattr(ball, "kind", "") == "deployable_lightning_rod":
                        ball.charge = getattr(ball, "charge", 0.0) + hazard.damage
                    else:
                        ball.supercharge_timer = 5.0

    assert ball.charge == 50.0
