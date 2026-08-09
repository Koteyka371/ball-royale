import pytest
import math
from ai.action import Action

class MockBall:
    def __init__(self, id, team, ball_type, x=0, y=0, stamina=100.0, max_stamina=100.0, hp=100.0):
        self.id = id
        self.team = team
        self.ball_type = ball_type
        self.x = x
        self.y = y
        self.stamina = stamina
        self.max_stamina = max_stamina
        self.hp = hp
        self.alive = True
        self.radius = 10.0
        self.skill = "dash"
        self.SKILL = "dash"
        self.active_skill = "dash"
        self.skill_timer = 0.0
        self.slow_timer = 0.0
        self.stamina_speed_burst_timer = 0.0
        self.dash_range_mult = 1.0

class MockWorld:
    def __init__(self, balls):
        self.balls = balls
        self.events = []
        self.arena = type('Arena', (), {'clamp_position': lambda self, x, y, r: (x, y, False)})()
        self.game_mode = None

def test_cluster_dash_max_stamina_discharge():
    # Setup ball at max stamina
    b1 = MockBall(1, "team1", "player", x=0, y=0, stamina=100, max_stamina=100)
    # The jump_radius is 200, cluster radius is 150 for discharge.
    # Enemy 1: directly hit (should take damage, no slow)
    e1 = MockBall(2, "team2", "player", x=5, y=0)
    # Enemy 2: not directly hit by first jump, but within 150 radius of b1's start
    e2 = MockBall(3, "team2", "player", x=100, y=100)
    # Enemy 3: out of discharge radius
    e3 = MockBall(4, "team2", "player", x=1000, y=1000)

    world = MockWorld([b1, e1, e2, e3])
    action = Action(b1, world)
    # Give action a way to get enemies
    action._get_enemies = lambda: [e for e in world.balls if getattr(e, "team", "") != b1.team and getattr(e, "hp", 0) > 0]

    # Just run it
    action._use_skill()

    assert b1.stamina_speed_burst_timer == 0.0 # Converted, so no burst
    # Check that events have electrical discharge
    assert any(ev.get("data", {}).get("type") == "electric_discharge" for ev in world.events)

    # Check hit status (e1 hit by dash)
    assert e1.hp < 100.0

    # e2 not hit by dash directly (b1 targets e1 first), but it's in slow radius (150)
    assert getattr(e2, "slow_timer", 0.0) > 0.0
