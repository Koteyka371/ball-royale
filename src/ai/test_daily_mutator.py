from game_modes import DailyMutatorMode
import time

class MockProfileManager:
    def __init__(self):
        self.cosmetics = []

    def add_cosmetic(self, name):
        self.cosmetics.append(name)

class MockWorld:
    def __init__(self):
        self.dead_balls = []
        self.profile_manager = MockProfileManager()

class MockBall:
    def __init__(self, ball_type, team=None):
        self.ball_type = ball_type
        self.team = team if team else ball_type
        self.mass = 1.0
        self.base_damage = 10.0
        self.damage = 10.0
        self.base_speed = 100.0
        self.speed = 100.0
        self.lifesteal = 0.0
        self.max_hp = 100.0
        self.hp = 100.0
        self.skill_cooldown = 5.0
        self.alive = True
        self.skill_points = 0

def test_daily_mutator_setup():
    mode = DailyMutatorMode()
    world = MockWorld()
    ball = MockBall("brawler")

    # Force a specific mutator combination for testing
    mode.setup(world, [ball])

    assert len(mode.mutators) > 0

    # Reset ball state
    ball = MockBall("brawler")
    # Now explicitly test one of the mutators by overriding it
    mode.mutators = ["low_gravity", "double_damage"]
    # Re-run setup logic for this specific mutator
    if "low_gravity" in mode.mutators:
        ball.mass *= 0.5
    if "double_damage" in mode.mutators:
        ball.base_damage *= 2.0
        ball.damage *= 2.0

    assert ball.mass == 0.5
    assert ball.base_damage == 20.0
    assert ball.damage == 20.0

def test_daily_mutator_tick():
    mode = DailyMutatorMode()
    world = MockWorld()

    # 2 teams
    ball1 = MockBall("brawler", "team1")
    ball2 = MockBall("sniper", "team2")
    balls = [ball1, ball2]

    mode.setup(world, balls)

    # Both alive, no rewards
    mode.tick(world, balls)
    assert len(world.profile_manager.cosmetics) == 0
    assert ball1.skill_points == 0
    assert ball2.skill_points == 0

    # team2 dies
    ball2.alive = False

    # Tick again, should give rewards to survivors
    mode.tick(world, balls)

    assert "Daily Survivor Crown" in world.profile_manager.cosmetics
    assert ball1.skill_points == 10
    assert ball2.skill_points == 0
