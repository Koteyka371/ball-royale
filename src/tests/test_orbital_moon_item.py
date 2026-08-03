import pytest
from ai.action import Action
from ai.game_modes import GameMode

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self, arena, balls):
        self.arena = arena
        self.balls = balls
        self.events = []

    def _deal_damage(self, attacker, target, dmg):
        target.hp -= dmg
        if target.hp <= 0:
            target.alive = False

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.radius = 15.0
        self.alive = True
        self.hp = 100
        self.inventory = []
        self.use_item = False

def test_orbital_moon_item():
    arena = MockArena()
    owner = MockBall(1, 100, 100)
    owner.inventory.append("orbital_moon_item")
    owner.use_item = True

    enemy = MockBall(2, 200, 200)

    world = MockWorld(arena, [owner, enemy])
    action = Action(owner, world)

    action.execute("attack", 0.016)

    assert "orbital_moon_item" not in owner.inventory
    assert len(arena.hazards) == 3
    for h in arena.hazards:
        assert getattr(h, "kind") == "orbital_moon"
        assert getattr(h, "owner_id") == owner.id

    gm = GameMode()
    gm.tick(world, [owner, enemy], 0.016)

    # move an enemy into the path
    m = arena.hazards[0]
    enemy.x = m.x
    enemy.y = m.y

    hp_before = enemy.hp
    gm.tick(world, [owner, enemy], 0.016)

    assert enemy.hp < hp_before
    assert len(arena.hazards) == 2 # one consumed
