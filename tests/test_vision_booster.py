import pytest

from ai.game_modes import BattleRoyaleMode
from ai.action import Action
from arena.procedural_arena import ProceduralArena

class MockWorld:
    def __init__(self):
        self.arena = ProceduralArena(1000, 1000)
        self.balls = []
        self.boosters = []
        self.tick = 0

class MockBall:
    def __init__(self):
        self.id = 1
        self.x = 500.0
        self.y = 500.0
        self.radius = 10.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.team = "A"
        self.speed = 100.0
        self.damage = 10.0
        self.base_damage = 10.0
        self.perception_radius = 250.0
        self.base_perception_radius = 250.0

class MockHazard:
    def __init__(self, kind, x, y, radius):
        self.id = 9999
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = radius
        self.active = True
        self.active = True


def test_collect_vision_booster():
    world = MockWorld()
    ball = MockBall()
    world.balls.append(ball)
    action = Action(ball, world)

    # Spawn a vision booster near the ball
    h = MockHazard("vision_booster", 510.0, 500.0, 30.0)
    world.arena.hazards.append(h)

    # Mock Action methods
    action._get_boosters = lambda: [h for h in world.arena.hazards if getattr(h, "active", True)]
    ball.x = 510.0
    ball.y = 500.0
    action._get_enemies = lambda: []
    action._get_allies = lambda: []

    # Execute collect_booster
    for _ in range(100): action._collect_booster(0.1)
    print("has_timer:", hasattr(ball, "vision_booster_timer"))
    print("ball.x:", ball.x)

    assert getattr(ball, "vision_booster_timer", 0) == 15.0
    assert getattr(ball, "vision_booster_applied", False) == True
    assert ball.base_perception_radius == 500.0
    assert ball.perception_radius == 500.0
    assert h not in world.arena.hazards

def test_dark_phase_with_vision_booster():
    mode = BattleRoyaleMode()
    world = MockWorld()
    ball = MockBall()
    ball.ball_type = "normal"
    world.balls.append(ball)

    # Setup dark phase
    mode.dark_phase_timer = 20.0
    mode.tick(world, world.balls, 0.1)

    assert mode.is_dark_phase == True
    assert ball.perception_radius == 60.0

    # Revert to normal
    mode.dark_phase_timer = 10.0
    mode.tick(world, world.balls, 0.1)
    assert mode.is_dark_phase == False
    assert ball.perception_radius == 250.0

    # Dark phase again, but this time with vision booster
    ball.vision_booster_timer = 15.0
    mode.dark_phase_timer = 20.0
    mode.tick(world, world.balls, 0.1)

    assert mode.is_dark_phase == True
    assert ball.perception_radius == 250.0 # Should be immune to 60.0 reduction
