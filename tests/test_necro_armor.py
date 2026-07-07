import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.action import Action
from ai.ball_types_necromancer import Necromancer

class MockWorld:
    def __init__(self):
        self.events = []
        self.dead_balls = []
        self.arena = type("MockArena", (), {"hazards": []})
        self.profile_manager = type("MockPM", (), {"is_nemesis": lambda a, b: False})
        self.balls = []

    def add_event(self, event_type, data):
        self.events.append({"type": event_type, "data": data})

    def _deal_damage(self, attacker, target, damage=None):
        if damage is None:
            damage = getattr(attacker, "damage", 10.0)
        target.hp -= damage


class MockBall:
    def __init__(self, id=1, ball_type="basic", hp=100.0, max_hp=100.0, damage=10.0, x=0, y=0, alive=True):
        self.id = id
        self.ball_type = ball_type
        self.hp = hp
        self.max_hp = max_hp
        self.damage = damage
        self.x = x
        self.y = y
        self.alive = alive
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 10.0


def test_bone_armor_stack_generation():
    world = MockWorld()
    necro = Necromancer(ball_id=1)
    world.balls.append(necro)

    action = Action(necro, world)

    # Initial state
    assert necro.bone_armor_stacks == 0
    assert necro.bone_armor_timer == 5.0

    # Tick 4.9 seconds - should not generate stack
    action.execute("idle", 4.9)
    assert necro.bone_armor_stacks == 0
    assert abs(necro.bone_armor_timer - 0.1) < 0.01

    # Tick 0.2 seconds - should cross the 0 threshold and generate stack
    action.execute("idle", 0.2)
    assert necro.bone_armor_stacks == 1
    assert abs(necro.bone_armor_timer - 5.0) < 0.01

    # Tick 15.0 seconds (3 more stacks) - max stacks should be 3
    action.execute("idle", 5.0)
    assert necro.bone_armor_stacks == 2
    action.execute("idle", 5.0)
    assert necro.bone_armor_stacks == 3
    action.execute("idle", 5.0)
    assert necro.bone_armor_stacks == 3


def test_bone_armor_damage_reduction():
    world = MockWorld()
    necro = Necromancer(ball_id=1)
    necro.bone_armor_stacks = 1
    necro.hp = 100.0
    world.balls.append(necro)

    attacker = MockBall(id=2, damage=15.0)
    world.balls.append(attacker)

    action = Action(attacker, world)

    # Attack with 15 damage should be reduced by 10
    action._attempt_damage(attacker, necro)

    assert necro.bone_armor_stacks == 0

    # Check if damage was dealt.
    # Because _attempt_damage usually just reduces HP or calls _deal_damage
    # The normal execution logic calculates new_hp inside the same function if no _deal_damage exists.
    # We passed a MockWorld with _deal_damage, so we check necro.hp
    # wait, _attempt_damage directly sets hp down by original_damage only if there's no _deal_damage or if it doesn't return early.
    # In action.py, it either calls _deal_damage or just relies on the caller.
    # Actually wait, _attempt_damage has a bunch of nested logic, let's just make sure the mock world catches it.

    # Note: _attempt_damage on Necromancer logic specifically checks if executed_by_necromancer, etc.
    # Let's just remove _deal_damage from MockWorld to let fallback hp subtraction happen if any,
    # or let MockWorld handle it.
    pass

# We will write a better test for damage reduction since _attempt_damage might be complex.
def test_bone_armor_damage_reduction_better():
    world = MockWorld()
    necro = Necromancer(ball_id=1)
    necro.bone_armor_stacks = 2
    necro.hp = 100.0

    attacker = MockBall(id=2, damage=15.0)
    attacker.attack_accuracy = 1.0 # guarantee hit

    # In action.py, after setting original_damage, it calls _deal_damage but relies on attacker.damage not original_damage by default?
    # Wait, looking at action.py:
    #             if hasattr(self.world, "_deal_damage"):
    #                 old_dmg_final = getattr(attacker, "damage", 10.0)
    #                 attacker.damage = original_damage
    #                 self.world._deal_damage(attacker, target)
    #                 attacker.damage = old_dmg_final
    # Yes, it sets attacker.damage = original_damage before calling _deal_damage.

    action = Action(attacker, world)

    action._attempt_damage(attacker, necro)

    assert necro.hp == 95.0 # 100 - (15 - 10)
    assert necro.bone_armor_stacks == 1

    # Second attack
    action._attempt_damage(attacker, necro)
    assert necro.hp == 90.0 # 95 - (15 - 10)
    assert necro.bone_armor_stacks == 0

    # Third attack - no stacks left, full damage
    action._attempt_damage(attacker, necro)
    assert necro.hp == 75.0 # 90 - 15
    assert necro.bone_armor_stacks == 0
