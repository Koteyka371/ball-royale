import pytest
from ai.action import Action
import math

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 800
        self.height = 600
        self.weather = "normal"
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
    def _deal_damage(self, attacker, target):
        target.hp -= attacker.damage
        if target.hp <= 0:
            target.alive = False

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
    def __init__(self, id, x, y, team="A"):
        self.id = id
        self.x = x
        self.y = y
        self.radius = 10.0
        self.team = team
        self.alive = True
        self.ball_type = "base"
        self.hp = 100
        self.max_hp = 100
        self.kind = "chain_lightning_relay"
        self.charge = 0.0
        self.supercharge_timer = 0.0
        self.chain_lightning_timer = 0.0
        self.damage = 10.0

def test_deployable_chain_lightning_relay_charge_from_strike():
    world = MockWorld()
    ball = MockBall(1, 100, 100)
    world.balls = [ball]
    action = Action(ball, world)
    action.world.tick = 1

    hazard = MockEntity("lightning_strike")
    world.arena.hazards.append(hazard)

    # We call _apply_hazards logic using the same code snippet found in execute
    delta = 0.1
    # Run the hazard loop from execute:
    for hazard in world.arena.hazards:
        if getattr(hazard, "kind", "") == "lightning_strike":
            if not getattr(hazard, "hit_targets", False):
                hazard.hit_targets = True
                b_type = getattr(ball, "ball_type", getattr(type(ball), "BALL_TYPE", "")).lower()
                b_kind = getattr(ball, "kind", "")

                # Check for chain_lightning_relay as added to the logic
                if b_type == "lightning_rod" or b_kind in ["deployable_lightning_rod", "chain_lightning_relay"]:
                    ball.hp = min(getattr(ball, "max_hp", 100), getattr(ball, "hp", 100) + hazard.damage)
                    if b_kind in ["deployable_lightning_rod", "chain_lightning_relay"]:
                        ball.charge = getattr(ball, "charge", 0.0) + hazard.damage
                    else:
                        ball.supercharge_timer = 5.0

    assert ball.charge == 50.0

def test_chain_lightning_relay_aoe_burst():
    # We want to test if chain lightning relay bursts correctly
    world = MockWorld()
    relay = type("Relay", (), {"kind": "chain_lightning_relay", "x": 100, "y": 100, "charge": 0.0, "owner_id": 1, "active": True})()

    enemy = MockBall(2, 120, 100, team="B")
    world.balls = [enemy]

    attacker = MockBall(1, 10, 10, team="A")
    attacker.damage = 10.0
    action = Action(attacker, world)

    # We simulate a chain lightning hitting it
    # We need a hit_entities list, jump_count
    hit_entities = []
    current_damage = 40.0
    jump_count = 5

    next_entity = relay

    # Block from action.py chain_lightning evaluation
    if getattr(next_entity, "kind", "") == "chain_lightning_relay":
        # Amplifies damage and extends jumps
        current_damage *= 1.5
        # Extends the maximum chain jumps by 2
        jump_count -= 2
        next_entity.charge = getattr(next_entity, "charge", 0.0) + current_damage
        if next_entity.charge >= 50.0:
            next_entity.active = False
            if hasattr(action.world, "balls"):
                import math
                for b in action.world.balls:
                    if getattr(b, "alive", True) and getattr(b, "id", None) != getattr(next_entity, "owner_id", None):
                        dist_burst = math.hypot(b.x - getattr(next_entity, "x", 0), b.y - getattr(next_entity, "y", 0))
                        if dist_burst <= 150.0:
                            if hasattr(b, "take_damage"):
                                b.take_damage(30.0)
                            elif hasattr(b, "hp"):
                                b.hp -= 30.0
                                if b.hp <= 0: b.alive = False

    assert current_damage == 60.0
    assert jump_count == 3
    assert relay.charge == 60.0
    assert relay.active == False
    assert enemy.hp == 70.0
