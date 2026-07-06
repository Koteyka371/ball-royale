import pytest
from arena.arena_types import ThunderstormArena
from ai.action import Action

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.radius = 10.0
        self.vx = 0.0
        self.vy = 0.0
        self.speed = 100.0
        self.base_speed = 100.0
        self.hp = 1000.0
        self.alive = True
        self.team = "A"
        self.ball_type = "normal"
        self.is_flying = False
        self.stutter_timer = 0.0
        self.perception_radius = 200.0

class MockWorld:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tick = 0
        self.balls = []
        self.arena = ThunderstormArena(2000.0, seed=42)

def test_lightning_strike_warning_and_transition():
    world = MockWorld(2000, 2000)

    # Tick loop to bypass safe zone or anything that prevents update
    world.arena.hazards = []

    world.tick += 1
    # Trigger lightning
    world.arena.lightning_timer = 2.0
    world.arena.update_zone(world.tick, 0.0)

    warnings = [h for h in world.arena.hazards if getattr(h, "kind", "") == "lightning_warning"]
    assert len(warnings) == 1
    warning = warnings[0]
    assert warning.damage == 0.0
    assert getattr(warning, "duration", 0.0) == 1.0

    # Tick down warning
    world.arena.update_zone(world.tick + 1, 0.5)
    assert getattr(warning, "kind", "") == "lightning_warning"
    assert getattr(warning, "duration", 0.0) == 0.5

    world.arena.update_zone(world.tick + 2, 0.6)

    # Now it should be a lightning strike
    lightnings = [h for h in world.arena.hazards if getattr(h, "kind", "") == "lightning"]
    assert len(lightnings) == 1
    lightning = lightnings[0]
    assert getattr(lightning, "duration", 0.0) == 0.5
    assert lightning.damage == 300.0

def test_lightning_strike_collision():
    ball = MockBall(1, 100.0, 100.0)
    world = MockWorld(2000, 2000)
    world.balls.append(ball)
    world.arena.hazards = []

    # Create a lightning hazard on top of the ball
    from arena.procedural_arena import Hazard
    lightning = Hazard(id=999, x=100.0, y=100.0, radius=60.0, kind="lightning", damage=300.0)
    setattr(lightning, "duration", 0.5)
    world.arena.hazards.append(lightning)

    action = Action(ball, world)

    assert ball.hp == 1000.0
    assert ball.stutter_timer == 0.0

    action.execute("none", 0.0) # Using 0 delta to check initial apply without decrement

    assert ball.stutter_timer == 2.0
    assert ball.id in lightning.hit_ids
    assert abs(ball.hp - 700.0) < 0.01

    # Second tick, damage shouldn't re-apply
    action.execute("none", 0.016)
    assert abs(ball.hp - 700.0) < 0.01
