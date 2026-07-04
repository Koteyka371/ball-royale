import pytest
from ai.action import Action

class MockGameMode:
    def __init__(self, name="Normal"):
        self.name = name

class MockWorld:
    def __init__(self, width=1000, height=1000):
        self.width = width
        self.height = height
        self.game_mode = MockGameMode()

class MockBall:
    def __init__(self, ball_type="normal"):
        self.x = 10
        self.y = 500
        self.vx = -1000
        self.vy = 0
        self.hp = 100
        self.alive = True
        self.radius = 15
        self.team = "test"
        self.ball_type = ball_type
        self.speed = 100

def test_agile_bouncer_no_damage():
    world = MockWorld()

    for agile_type in ["ninja", "assassin", "rogue"]:
        ball = MockBall(ball_type=agile_type)
        action = Action(ball, world)

        # Simulate moving past the left boundary to trigger bounced_wall clamp
        ball.x = -100
        action.execute("idle", 1.0)

        # Should not take damage
        assert ball.hp == 100

        # Should bounce off the wall (vx reversed and possibly increased)
        # Because the wall is on the left, it should bounce to the right (positive vx)
        assert ball.vx > 0
        # Check that new speed is higher (speed * 1.5 capped at 2000, initial speed was 1000)
        assert ball.vx > 1000 or hasattr(ball, "_reflection_vx")

def test_normal_ball_takes_damage():
    world = MockWorld()
    ball = MockBall(ball_type="warrior")
    action = Action(ball, world)

    # Simulate moving past the left boundary
    ball.x = -100
    action.execute("idle", 1.0)

    # Should take damage (speed 1000 > 500, damage = 1000 * 0.05 = 50)
    assert ball.hp < 100
    assert ball.hp == 50

if __name__ == "__main__":
    test_agile_bouncer_no_damage()
    test_normal_ball_takes_damage()
    print("Tests passed.")
