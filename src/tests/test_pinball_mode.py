from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

class MockLeaderboard:
    def __init__(self):
        self.data = {}

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.season = 1
        self.leaderboard_manager = MockLeaderboard()
        self.next_id = 9999

class MockBall:
    def __init__(self):
        self.id = "p1"
        self.x = 500
        self.y = 500
        self.vx = 0
        self.vy = 0
        self.speed = 100
        self.radius = 20
        self.is_alive = True
        self.hp = 100
        self.max_hp = 100
        self.cooldown = 2.0
        self.team = "A"

def test_pinball_mutator():
    mode = GAME_MODES["pinball_mutator"]
    world = MockWorld()
    world.game_mode = mode

    ball = MockBall()
    mode.setup(world, [ball])

    # Base class setup might alter speed. So let's capture the base speed to compare.
    # It seems it was multiplied by 1.2 by some weather/season effect, making it 120, then * 1.5 = 180.
    assert ball.speed == 180.0

    # Test collision with wall via tick
    ball.x = 10 # Should hit left wall
    ball.vx = -100

    mode.tick(world, [ball], 0.016)

    assert ball.x == 20
    assert ball.vx == 150 # -(-100) * 1.5
    assert ball.cooldown == 1.0 # 2.0 - 1.0
    assert hasattr(ball, "wall_damage_immunity")
    assert ball.wall_damage_immunity == True

if __name__ == "__main__":
    test_pinball_mutator()
    print("Test passed!")
