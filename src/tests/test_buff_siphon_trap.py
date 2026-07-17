import pytest
from ai.action import Action

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.tick = 0

class MockArena:
    def __init__(self):
        self.hazards = []

class MockHazard:
    def __init__(self, id, x, y, kind, radius=60.0, owner_id=1, owner_team="teamA"):
        self.id = id
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = radius
        self.owner_id = owner_id
        self.owner_team = owner_team

class MockBall:
    def __init__(self, id, x, y, team="teamA"):
        self.id = id
        self.x = x
        self.y = y
        self.radius = 10.0
        self.hp = 100.0
        self.alive = True
        self.ball_type = "basic"
        self.team = team
        self.vx = 0.0
        self.vy = 0.0
        self.suspended_projectiles = []
        self.state_history = []
        self.speed_boost_timer = 0.0
        self.shield_duration = 0.0
        self.combo_multiplier = 1.0

def test_buff_siphon_trap():
    world = MockWorld()
    owner_ball = MockBall(1, 0, 0, "teamA")
    victim_ball = MockBall(2, 10, 10, "teamB")

    # Give victim buffs
    victim_ball.speed_boost_timer = 5.0
    victim_ball.combo_multiplier = 2.0

    world.balls = [owner_ball, victim_ball]

    trap = MockHazard(1, 10, 10, "buff_siphon_trap", radius=60.0, owner_id=1, owner_team="teamA")
    world.arena.hazards.append(trap)

    action = Action(victim_ball, world)

    # Delta of 0.1
    # Decay for timer is 0.1, siphon is 2.0 * 0.1 = 0.2. Total reduction = 0.3
    # Combo multiplier doesn't naturally decay, siphon is 0.5 * 0.1 = 0.05
    world.tick = 1
    action.execute("idle", 0.1)

    # Due to normal decay of 0.1 and siphon of 0.2:
    assert round(victim_ball.speed_boost_timer, 2) == round(5.0 - 0.1 - 0.2, 2)
    assert round(victim_ball.combo_multiplier, 2) == round(2.0 - 0.05, 2)

    # Check that owner gained buffs
    # owner gained 0.2 timer on either speed or shield
    assert owner_ball.speed_boost_timer >= 0.2 or owner_ball.shield_duration >= 0.2
    assert round(owner_ball.combo_multiplier, 2) == 1.05

if __name__ == "__main__":
    pytest.main(["-v", "src/tests/test_buff_siphon_trap.py"])
