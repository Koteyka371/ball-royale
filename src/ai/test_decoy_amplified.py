import pytest
import sys
import os
sys.path.append(os.path.abspath('src'))
from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000
        self.height = 1000
    def clamp_position(self, x, y, r):
        return x, y, False

class MockWorld:
    def __init__(self, arena, balls=None):
        self.arena = arena
        self.balls = balls if balls else []
        self.events = []
        self.tick = 0
    def add_event(self, event_type, data):
        pass
    def get_nearby_entities(self, b, r):
        return {'boosters': [], 'hazards': [], 'enemies': [], 'allies': [], 'items': []}

class MockBall:
    def __init__(self, id, x, y, team="team_a"):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.alive = True
        self.hp = 100.0
        self.max_hp = 100.0
        self.vx = 0
        self.vy = 0
        self.speed = 0
        self.ball_type = "base"
        self.traits = []

def test_amplified_decoy_explosion():
    arena = MockArena()

    decoy1 = MockBall(id=1, x=100, y=100, team="team_a")
    decoy1.is_decoy = True
    decoy1.decoy_type = "explosive"
    decoy1.decoy_timer = 5.0
    decoy1.owner_id = 999
    decoy1.hp = 0  # Trigger explosion

    decoy2 = MockBall(id=2, x=120, y=100, team="team_a")
    decoy2.is_decoy = True
    decoy2.decoy_type = "explosive"
    decoy2.decoy_timer = 5.0
    decoy2.owner_id = 1000  # Different owner ID to prevent simultaneous detonation logic
    decoy2.hp = 100

    # Place enemy far away so decoy1 doesn't hit it, only decoy2
    enemy = MockBall(id=3, x=220, y=100, team="team_b")

    world = MockWorld(arena, [decoy1, decoy2, enemy])

    # Tick 1: decoy1 explodes, damaging enemy? No, radius is 100, distance is 120.
    action1 = Action(decoy1, world)
    action1.execute("chase", 1.0)

    assert getattr(decoy1, "_decoy_exploded", False) is True
    assert getattr(decoy2, "hp", 100) == 0
    assert getattr(decoy2, "amplified_explosion", False) is True
    # In MockWorld, distance from decoy1 (100, 100) to enemy (220, 100) is 120. Radius is 100.
    # But wait, action.py iterates through `self.world.balls`. Oh, `b` is from `self.world.balls`.
    # Let's check enemy.hp
    # assert enemy.hp == 100

    # Oh! `action.py` global decoy check looks at ALL decoys in `self.world.balls` that are dead.
    # Decoy1 is dead, explodes.
    # Decoy2 is killed by Decoy1, making its HP = 0.
    # In the SAME tick loop, since Decoy2 is in `self.world.balls`, and its HP is now 0, it WILL ALSO explode!
    # Because `b` loops over `world.balls`.
    # decoy2 explosion has `amplified_explosion=True`, `volatile_decoy=True` (radius 150*1.5 = 225, damage 80*1.5 = 120).
    # Enemy is at (220, 100), distance to decoy2 (120, 100) is 100.
    # So enemy takes 120 damage! Enemy hp: 100 - 120 = -20!

    # We can just check the final state after one execute!
    assert getattr(decoy2, "_decoy_exploded", False) is True
    assert getattr(decoy2, "amplified_explosion", False) is True
    assert enemy.hp == 100 - 120 # -20.0
