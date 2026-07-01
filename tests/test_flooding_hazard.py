import pytest
from arena.procedural_arena import ProceduralArena, Hazard
from ai.action import Action

class MockArena:
    def __init__(self):
        self.is_raining = True
        self.hazards = []

class MockWorld:
    def __init__(self, arena):
        self.arena = arena
        self.balls = []

class MockBall:
    def __init__(self, x, y, cosmetic=""):
        self.id = 1
        self.x = x
        self.y = y
        self.radius = 10.0
        self.traits = []
        self.stamina = 100.0
        self.max_stamina = 100.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.speed = 100.0
        self.base_speed = 100.0
        self.is_dashing = False
        self.cosmetic = cosmetic

def test_water_flood_generation():
    arena = ProceduralArena(2000, 5)
    arena.is_raining = True

    # Try spawning flood hazard
    import random
    random.seed(42)  # Will trigger random.random() < 0.2 if needed
    for _ in range(5):
        arena.update_zone(120, 1.0)

    floods = [h for h in arena.hazards if getattr(h, "kind", "") == "water_flood"]
    assert len(floods) > 0
    assert floods[0].target_radius > 0.0

def test_water_flood_action_slow():
    arena = MockArena()
    arena.hazards.append(Hazard(id=1, x=50, y=50, radius=50, kind="water_flood", damage=0.0))
    world = MockWorld(arena)

    # Non-aquatic ball
    ball = MockBall(50, 50)
    original_speed = ball.base_speed
    world.balls.append(ball)

    action = Action(ball, world)
    action.execute("idle", 1.0)

    # Speed should be reduced
    assert ball.speed <= original_speed * 0.3

def test_water_flood_action_floatie():
    arena = MockArena()
    arena.hazards.append(Hazard(id=1, x=50, y=50, radius=50, kind="water_flood", damage=0.0))
    world = MockWorld(arena)

    # Aquatic ball
    ball = MockBall(50, 50, cosmetic="floatie")
    world.balls.append(ball)

    action = Action(ball, world)
    action.execute("idle", 1.0)

    # Speed should not be reduced
    assert ball.speed == ball.base_speed
