import pytest
from ai.action import Action
from ai.game_modes import GAME_MODES

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

class MockHazard:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = 15.0
        self.is_reversed = False

class MockBall:
    def __init__(self, x, y, skill="grapple_hook"):
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
        self.vx = 0.0
        self.vy = 0.0
        self.mass = 1.0

def test_reversing_node_grapple_pull():
    world = MockWorld()
    ball = MockBall(500, 500)
    ball.inventory.append("grapple_hook")
    world.balls.append(ball)

    node = MockHazard(600, 500, "reversing_grapple_node")
    world.arena.hazards.append(node)

    action = Action(ball, world)
    action._use_skill()

    # Grapple pull (ball.x should increase towards 600)
    assert ball.vx > 0
    assert node in world.arena.hazards # Should not break

def test_reversing_node_collision_reverse():
    world = MockWorld()
    ball = MockBall(500, 500)
    world.balls.append(ball)

    # Collision requires dist < ball_radius + node_radius = 10 + 15 = 25
    node = MockHazard(510, 500, "reversing_grapple_node")
    world.arena.hazards.append(node)

    action = Action(ball, world)
    action._resolve_collisions()

    assert getattr(node, "is_reversed", False) is True
    assert ball.vx < 0 # pushed away (nx is roughly -1)

def test_reversing_node_grapple_slingshot():
    world = MockWorld()
    ball = MockBall(500, 500)
    ball.inventory.append("grapple_hook")
    world.balls.append(ball)

    node = MockHazard(600, 500, "reversing_grapple_node")
    node.is_reversed = True
    world.arena.hazards.append(node)

    action = Action(ball, world)
    action._use_skill()

    # Slingshot push (vx should be negative)
    assert ball.vx < 0
    assert node in world.arena.hazards # Should not break
