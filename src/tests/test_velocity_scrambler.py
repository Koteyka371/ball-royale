import pytest
from ai.action import Action
from ai.game_modes import GameMode
from arena.procedural_arena import Hazard

class MockBall:
    def __init__(self, x=50.0, y=50.0, team="red", b_id=1, hp=100):
        self.id = b_id
        self.x = x
        self.y = y
        self.team = team
        self.inventory = []
        self.alive = True
        self.ball_type = team
        self.hp = hp
        self.radius = 15.0
        self.vx = 100.0
        self.vy = -100.0

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000.0
        self.height = 1000.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.tick = 0
        self.events = []

    def add_event(self, event_type, data):
        self.events.append({"type": event_type, "data": data})

    def get_nearby_entities(self, ball, radius):
        return [b for b in self.balls if b != ball and b.alive]

def test_deployable_velocity_scrambler_deployment():
    world = MockWorld()
    ball = MockBall(x=100.0, y=100.0, team="red")
    enemy = MockBall(x=120.0, y=120.0, team="blue")
    ball.inventory.append("deployable_velocity_scrambler_trap")
    world.balls = [ball, enemy]

    action = Action(ball, world)
    action.execute("attack", 0.1)

    assert "deployable_velocity_scrambler_trap" not in ball.inventory
    assert len(world.arena.hazards) == 1
    hazard = world.arena.hazards[0]
    assert hazard.kind == "deployable_velocity_scrambler_trap"
    assert hazard.x == 100.0
    assert hazard.y == 100.0

def test_deployable_velocity_scrambler_logic():
    world = MockWorld()
    b1 = MockBall(x=100.0, y=100.0, b_id=1)
    # Outside radius
    b2 = MockBall(x=500.0, y=500.0, b_id=2)
    world.balls = [b1, b2]

    hazard = Hazard(1, 100.0, 100.0, 80.0, "deployable_velocity_scrambler_trap", 0.0)
    world.arena.hazards = [hazard]

    mode = GameMode()
    mode.apply_dynamic_traits(world, world.balls, 0.1)

    # B2 should be unaffected
    assert b2.x == 500.0 and b2.y == 500.0
    assert b2.vx == 100.0

    # B1 should be teleported and have velocity reduced
    assert b1.x != 100.0 or b1.y != 100.0
    assert b1.x >= 15.0 and b1.x <= 985.0
    assert abs(b1.vx - 30.0) < 0.01
    assert abs(b1.vy - (-30.0)) < 0.01
    assert getattr(b1, "vel_scramble_cd_1") == 2.0
