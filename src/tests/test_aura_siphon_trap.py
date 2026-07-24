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

        self.aura_booster_timer = 0.0
        self.aura_amplifier_timer = 0.0
        self.vampiric_aura_timer = 0.0

        self.base_speed = 100
        self.base_damage = 10
        self._base_speed_set = True
        self.speed_multiplier = 1.0
        self.damage_multiplier = 1.0

def test_aura_siphon_trap():
    world = MockWorld()
    owner_ball = MockBall(1, 0, 0, "teamA")
    victim_ball = MockBall(2, 10, 10, "teamB")

    victim_ball.aura_booster_timer = 5.0
    victim_ball.aura_amplifier_timer = 5.0

    world.balls = [owner_ball, victim_ball]

    trap = MockHazard(1, 10, 10, "aura_siphon_trap", radius=60.0, owner_id=1, owner_team="teamA")
    world.arena.hazards.append(trap)

    action = Action(victim_ball, world)

    world.tick = 1
    action.execute("idle", 0.1)

    assert round(victim_ball.aura_booster_timer, 2) == round(5.0 - 0.3, 2)
    assert round(victim_ball.aura_amplifier_timer, 2) == round(5.0 - 0.3, 2)
    assert (owner_ball.aura_booster_timer + owner_ball.aura_amplifier_timer + owner_ball.vampiric_aura_timer) >= 0.39

if __name__ == "__main__":
    pytest.main(["-v", "src/tests/test_aura_siphon_trap.py"])
