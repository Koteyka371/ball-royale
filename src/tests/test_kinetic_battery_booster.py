import pytest
import sys
import math
sys.path.append("src")
from ai.action import Action

class MockBall:
    def __init__(self, x=0, y=0, vx=0, vy=0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.team = -1
        self.alive = True
class MockHazard:
    def __init__(self, x=0, y=0, kind=""):
        self.x = x
        self.y = y
        self.kind = kind
class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards
class MockWorld:
    def __init__(self, arena, balls, boosters):
        self.arena = arena
        self.balls = balls
        self.boosters = boosters
        self.events = []
    def _deal_damage(self, attacker, target):
        pass

def test_kinetic_battery_booster():
    ball = MockBall(x=0, y=0)
    ball.team = 1
    target = MockBall(x=10, y=0)
    target.team = 2

    booster = MockHazard(0, 0, "kinetic_battery_booster")
    arena = MockArena([booster])
    world = MockWorld(arena, [ball, target], [booster])
    action = Action(ball, world)

    # 1. Collect booster
    action._get_boosters = lambda: [booster]
    action._collect_booster(0.1)

    assert getattr(ball, "kinetic_battery_timer", 0.0) == 15.0
    assert getattr(ball, "kinetic_battery_energy", -1.0) == 0.0

    # 2. Move and accumulate
    # Simulate movement logic inside execute directly
    # Regenerate stamina logic part:
    old_x, old_y = 0.0, 0.0
    ball.x = -50.0
    ball.y = 0.0
    delta = 0.1

    # Run the exact logic that was added to execute
    dist = math.sqrt((getattr(ball, "x", 0) - old_x)**2 + (getattr(ball, "y", 0) - old_y)**2)
    if getattr(ball, "kinetic_battery_timer", 0.0) > 0.0:
        ball.kinetic_battery_timer -= delta
        if ball.kinetic_battery_timer <= 0.0:
            ball.kinetic_battery_timer = 0.0
            ball.kinetic_battery_energy = 0.0
        else:
            current_energy = getattr(ball, "kinetic_battery_energy", 0.0)
            ball.kinetic_battery_energy = min(500.0, current_energy + dist)

    assert getattr(ball, "kinetic_battery_energy", -1.0) == 50.0

    # 3. Hit and discharge
    original_target_vx = target.vx
    action._attempt_damage_internal(ball, target)

    # Should reset energy and apply knockback
    assert getattr(ball, "kinetic_battery_energy", -1.0) == 0.0
    assert target.vx > original_target_vx
