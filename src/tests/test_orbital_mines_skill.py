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

    def add_event(self, type, data):
        self.events.append((type, data))

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.alive = True
        self.hp = 100
        self.radius = 15.0

    def take_damage(self, dmg):
        self.hp -= dmg
        if self.hp <= 0:
            self.alive = False

def test_orbital_mines_skill():
    arena = MockArena()
    owner = MockBall(1, 100, 100)
    enemy1 = MockBall(2, 500, 500) # out of range
    enemy2 = MockBall(3, 150, 100) # within 150 range

    world = MockWorld(arena, [owner, enemy1, enemy2])
    action = Action(owner, world)

    # 1. Test Spawning
    owner.skill = "orbital_mines"
    action.execute("use_skill", 0.016)

    assert len(arena.hazards) == 3
    for h in arena.hazards:
        assert getattr(h, "kind") == "player_orbital_mine"
        assert getattr(h, "owner_id") == owner.id
        assert getattr(h, "mine_state") == "orbiting"

    gm = GameMode()

    # 2. Test Orbiting and Target Acquisition
    gm.tick(world, [owner, enemy1, enemy2], 1.0)

    # Should acquire enemy2 which is within 150 range
    mines_seeking = [h for h in arena.hazards if getattr(h, "mine_state") == "seeking"]
    assert len(mines_seeking) == 3
    for m in mines_seeking:
        assert getattr(m, "target_id") == enemy2.id

    # 3. Test Seeking and Detonation
    # Move mine right on top of enemy2
    m = mines_seeking[0]
    m.x = enemy2.x
    m.y = enemy2.y

    hp_before = enemy2.hp
    gm.tick(world, [owner, enemy1, enemy2], 1.0)

    assert enemy2.hp < hp_before # Took damage
    assert len(world.events) > 0 # Explosion event
    assert m not in arena.hazards # Mine consumed
