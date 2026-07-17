import pytest
from ai.action import Action

class MockArena:
    def __init__(self):
        self.is_raining = False
        self.is_foggy = False
        self.hazards = []
        self.weather = "clear"
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.get_nearby_entities = lambda b, r: [e for e in self.balls if getattr(e, "alive", True)]

class MockBall:
    def __init__(self, id, x, y, hp=100, team="blue", ball_type="elementalist"):
        self.id = id
        self.x = float(x)
        self.y = float(y)
        self.hp = float(hp)
        self.team = team
        self.alive = True
        self.ball_type = ball_type
        self.BALL_TYPE = ball_type
        self.damage = 24.0
        self.active_skill = "lightning_strike"
        self.skill_timer = 0.0
        self.stun_timer = 0.0
        self.perception_radius = 250.0
        self.is_stunned = False
        self.stealth = False
        self.invisible = False
        self.is_invisible = False

    def take_damage(self, amount):
        self.hp -= amount

def test_lightning_strike_bounce_damage():
    world = MockWorld()

    # Attacker
    attacker = MockBall(1, 0, 0, team="blue", ball_type="elementalist")
    world.balls.append(attacker)

    # Targets (placed within chain range of 150 of each other)
    t0 = MockBall(2, 50, 0, hp=100, team="red", ball_type="enemy")
    t1 = MockBall(3, 100, 0, hp=100, team="red", ball_type="enemy")
    t2 = MockBall(4, 150, 0, hp=100, team="red", ball_type="enemy")
    t3 = MockBall(5, 200, 0, hp=100, team="red", ball_type="enemy")

    # Not in range for the fourth jump (max jumps is 3 anyway)
    t4 = MockBall(6, 400, 0, hp=100, team="red", ball_type="enemy")

    world.balls.extend([t0, t1, t2, t3, t4])

    action = Action(attacker, world)
    # Mock particles method
    action._spawn_skill_particles = lambda x: None

    # Execute skill
    action.execute("use_skill", 1.0)

    # Calculate expected hp
    expected_hp0 = 100 - 24.0
    expected_hp1 = 100 - (24.0 * 0.8) # 19.2
    expected_hp2 = 100 - (19.2 * 0.8) # 15.36
    expected_hp3 = 100 - (15.36 * 0.8) # 12.288

    assert abs(t0.hp - expected_hp0) < 0.01, f"Expected {expected_hp0}, got {t0.hp}"
    assert abs(t1.hp - expected_hp1) < 0.01, f"Expected {expected_hp1}, got {t1.hp}"
    assert abs(t2.hp - expected_hp2) < 0.01, f"Expected {expected_hp2}, got {t2.hp}"
    assert abs(t3.hp - expected_hp3) < 0.01, f"Expected {expected_hp3}, got {t3.hp}"
    assert t4.hp == 100, "Target 4 should not be damaged"

if __name__ == "__main__":
    test_lightning_strike_bounce_damage()
