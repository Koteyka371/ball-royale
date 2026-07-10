import pytest
from ai.action import Action

class MockBall:
    def __init__(self, id=1, x=0, y=0, team="red"):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.inventory = []
        self.alive = True
        self.base_speed = 0.0
        self.speed = 0.0
        self.stun_timer = 0.0
        self.poison_timer = 0.0
        self.frozen_timer = 0.0
        self.slow_timer = 0.0

class MockHazard:
    def __init__(self, kind, x, y, owner_id=None):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = 15.0
        self.owner_id = owner_id

class MockArena:
    def __init__(self):
        self.hazards = []

    def clamp_position(self, x, y, r):
        return x, y, False

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.balls = []

    def get_nearby_entities(self, ball, radius):
        return {
            'boosters': self.boosters,
            'hazards': self.arena.hazards,
            'enemies': []
        }

def test_booster_trap_pickup():
    world = MockWorld()
    ball = MockBall()
    world.balls.append(ball)

    trap_item = MockHazard("booster_trap_item", 5, 5)
    world.boosters.append(trap_item)

    action = Action(ball, world)
    action._collect_booster(1.0)

    assert "booster_trap" in ball.inventory
    assert trap_item not in world.boosters

def test_booster_trap_deploy():
    world = MockWorld()
    ball = MockBall()
    ball.inventory.append("booster_trap")
    world.balls.append(ball)

    action = Action(ball, world)
    try:
        action.execute("wander", 1.0)
    except Exception:
        pass

    assert "booster_trap" not in ball.inventory
    assert len(world.arena.hazards) == 1
    assert world.arena.hazards[0].kind == "placed_booster_trap"
    assert world.arena.hazards[0].owner_id == ball.id

def test_booster_trap_enemy_trigger():
    world = MockWorld()
    ball = MockBall(id=2)
    world.balls.append(ball)

    placed_trap = MockHazard("placed_booster_trap", 5, 5, owner_id=1)
    world.boosters.append(placed_trap) # put in boosters so it gets collected

    action = Action(ball, world)
    action._collect_booster(1.0)

    assert (ball.poison_timer > 0) or (ball.stun_timer > 0) or (ball.frozen_timer > 0) or (ball.slow_timer > 0)
    assert placed_trap not in world.arena.hazards
