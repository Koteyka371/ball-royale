import pytest
import math
from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.game_mode = None

    def get_nearby_entities(self, ball, radius):
        return {"enemies": [b for b in self.balls if b != ball]}

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.id = 1
        self.radius = 10.0
        self.speed = 100.0

def test_bouncy_zone_hazard_knockback_multiplier():
    world = MockWorld()
    b1 = MockBall(50, 50)
    world.balls.append(b1)

    # Adding b2 exactly touching b1 so overlap is > 0 and collisions resolve
    b2 = MockBall(50, 60)
    b2.id = 2
    world.balls.append(b2)

    action = Action(b1.id, world)
    action.ball = b1

    class MockHazard:
        def __init__(self, x, y, r):
            self.kind = "bouncy_zone"
            self.x = x
            self.y = y
            self.radius = r
            self.active = True

    # First without bouncy_zone
    b1_start_y = b1.y
    action._resolve_collisions()
    displacement_normal = abs(b1.y - b1_start_y)

    # Reset
    b1.y = 50
    b2.y = 60

    # Now add bouncy zone
    h = MockHazard(50, 50, 50)
    world.arena.hazards.append(h)

    # Action's execute would normally process hazards to set the flag, let's just run that block
    action._apply_hazards = getattr(action, "_apply_hazards", lambda d, s: None)

    # Simulate the hazard loop from execute()
    if hasattr(world, "arena") and hasattr(world.arena, "hazards"):
        in_bouncy_zone = False
        for hazard in world.arena.hazards:
            if hazard.kind == "bouncy_zone" and hazard.active:
                dx = hazard.x - b1.x
                dy = hazard.y - b1.y
                if (dx*dx + dy*dy) <= hazard.radius**2:
                    in_bouncy_zone = True
        b1.in_bouncy_zone = in_bouncy_zone

    action._resolve_collisions()
    displacement_bouncy = abs(b1.y - b1_start_y)

    assert displacement_bouncy > displacement_normal * 4.9, "Bouncy zone should apply 5.0 knockback multiplier"
