import pytest
from ai.action import Action

class MockBall:
    def __init__(self, id, team, ball_type):
        self.id = id
        self.team = team
        self.ball_type = ball_type
        self.x = 100.0
        self.y = 100.0
        self.radius = 20.0
        self.alive = True
        self.aura_well_buff_timer = 3.0
        self.speed_multiplier = 1.0
        self.damage_multiplier = 1.0

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.balls = []

def test_action_aura_well_buff():
    b = MockBall(1, "team1", "basic")
    world = MockWorld()
    world.balls.append(b)

    action = Action(b, world)

    # Run execute once
    action.execute("idle", 0.1)

    # Should apply the buff
    assert b.speed_multiplier == 1.5
    assert b.damage_multiplier == 1.5
    assert b.aura_well_buff_timer == 2.9

    # Now simulate until timer runs out
    b.aura_well_buff_timer = 0.05
    # Reset multipliers back to 1.0 since they are applied dynamically per tick (or test that it returns to normal)
    # Actually wait. If we just apply `self.ball.speed_multiplier = getattr(self.ball, "speed_multiplier", 1.0) * 1.5` every tick, it will accumulate over time if we don't reset it!
    # Ah! That's correct. We need to reset it before _execute_internal, OR we don't multiply it, we just apply it.
