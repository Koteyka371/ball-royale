import pytest
from ai.game_modes import GAME_MODES
from ai.action import Action

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.width = 1000
        self.height = 1000
        self.balls = []
        self.items = []
        self.events = []
        self.next_id = 1000

class MockEntity:
    def __init__(self, x, y, alive=True):
        self.x = x
        self.y = y
        self.alive = alive

class MockBall:
    def __init__(self, x, y, skill="grapple"):
        self.x = x
        self.y = y
        self.skill = skill
        self.skill_cooldown = 5.0
        self.skill_timer = 0.0
        self.alive = True
        self.team = 1
        self.id = 1
        self.hp = 100
        self.inventory = []

def test_grapple_node_spawn():
    mode = GAME_MODES["grapple_node"]
    world = MockWorld()
    mode.setup(world, [])

    assert len(world.arena.hazards) == 0
    mode.tick(world, [], 6.0)
    assert len(world.arena.hazards) == 3
    assert world.arena.hazards[0].kind == "grapple_node"

def test_grapple_node_hook():
    world = MockWorld()
    ball = MockBall(500, 500)
    ball.inventory.append("grapple_hook")
    world.balls.append(ball)

    class MockHazard:
        def __init__(self, x, y, kind):
            self.x = x
            self.y = y
            self.kind = kind
            self.radius = 15.0

    node = MockHazard(600, 500, "grapple_node")
    world.arena.hazards.append(node)

    action = Action(ball, world)
    action.execute("flee", 0.016)

    assert ball.x > 500.0  # Pulled towards node
    assert len(world.arena.hazards) == 0  # Node is broken
    assert len(world.items) == 1  # Material is dropped
    assert world.items[0]["kind"] == "material"
