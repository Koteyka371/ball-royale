import pytest
from ai.action import Action
import math

class MockEntity:
    def __init__(self, id, x, y, team, hp=100.0, is_clone=False, radius=10.0):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.hp = hp
        self.alive = True
        self.is_clone = is_clone
        self.radius = radius

class MockWorld:
    def __init__(self):
        self.entities = []
        self.game_mode = None

    def get_nearby_entities(self, entity, radius):
        nearby = []
        for e in self.entities:
            dist = math.hypot(e.x - entity.x, e.y - entity.y)
            if dist <= radius:
                nearby.append(e)
        return nearby

    def _deal_damage(self, attacker, target):
        damage = getattr(attacker, "damage", 10.0)
        target.hp -= damage
        if target.hp <= 0:
            target.alive = False

def test_clone_explosion_collision():
    world = MockWorld()

    # Create clone
    clone = MockEntity(1, 100.0, 100.0, "red", is_clone=True)

    # Create enemy overlapping clone (dist < 20)
    enemy = MockEntity(2, 110.0, 100.0, "blue")

    world.entities = [clone, enemy]

    action = Action(clone, world)

    # Resolve collisions should trigger clone explosion
    action._resolve_collisions()

    # Clone should be destroyed
    assert clone.hp <= 0
    assert not clone.alive

    # Enemy should take AoE damage (30.0)
    assert enemy.hp == 70.0

def test_clone_explosion_no_friendly_fire():
    world = MockWorld()

    # Create clone
    clone = MockEntity(1, 100.0, 100.0, "red", is_clone=True)

    # Create ally overlapping clone (dist < 20)
    ally = MockEntity(2, 110.0, 100.0, "red")

    world.entities = [clone, ally]

    action = Action(clone, world)

    # Resolve collisions
    action._resolve_collisions()

    # Clone should NOT explode when touching ally
    assert clone.hp == 100.0
    assert clone.alive

    # Ally should not take damage
    assert ally.hp == 100.0
