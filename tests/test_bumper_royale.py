import pytest
from ai.game_modes import BumperRoyaleMode
from ai.action import Action

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.game_mode = BumperRoyaleMode()
        self.balls = []

    def get_nearby_entities(self, entity, radius):
        return {"enemies": [b for b in self.balls if b != entity], "allies": []}

class MockBall:
    def __init__(self, x, y, hp=100.0, vx=0.0, vy=0.0, team="red"):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = 100.0
        self.vx = vx
        self.vy = vy
        self.alive = True
        self.radius = 10.0
        self.mass = 1.0
        self.team = team
        self.damage = 10.0
        self.ball_type = "normal"
        self.id = id(self)

def test_bumper_royale_initialization():
    mode = BumperRoyaleMode()
    assert mode.name == "Bumper Royale"
    assert "bumpers" in mode.description.lower()

def test_bumper_royale_tick_shrinking():
    world = MockWorld()
    mode = world.game_mode
    mode.setup(world, [])

    assert world.arena.width == 1000.0
    assert world.arena.height == 1000.0

    mode.tick(world, [], delta=60.0)
    assert world.arena.width == 500.0
    assert world.arena.height == 500.0

    mode.tick(world, [], delta=60.0)
    assert world.arena.width == 200.0
    assert world.arena.height == 200.0

def test_bumper_royale_boundary_kill():
    world = MockWorld()
    mode = world.game_mode
    b1 = MockBall(x=500.0, y=500.0) # Safe
    b2 = MockBall(x=-20.0, y=500.0) # Out of bounds
    b3 = MockBall(x=1500.0, y=500.0) # Out of bounds
    world.balls = [b1, b2, b3]

    mode.setup(world, world.balls)
    mode.tick(world, world.balls, 0.1)

    assert b1.alive == True
    assert b2.alive == False
    assert b3.alive == False

def test_bumper_royale_collision_damage():
    world = MockWorld()
    # High speed collision
    b1 = MockBall(x=500.0, y=500.0, vx=200.0, vy=0.0)
    b2 = MockBall(x=515.0, y=500.0, vx=-200.0, vy=0.0, team="blue")
    world.balls = [b1, b2]

    action1 = Action(b1, world)
    action1._resolve_collisions()

    # Total speed = 400. Damage = 400 * 0.05 = 20
    assert b1.hp < 100.0
    assert b2.hp < 100.0

    # Verify no standard attack damage
    mode = world.game_mode
    mode.apply_dynamic_traits(world, world.balls, 0.1)
    assert b1.damage == 0.0
    assert b2.damage == 0.0
