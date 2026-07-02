import pytest
from ai.action import Action
from ai.game_modes import MirrorWallsMode

class MockGameMode:
    def __init__(self, name="Normal"):
        self.name = name

class MockWorld:
    def __init__(self, width=1000, height=1000):
        self.width = width
        self.height = height
        self.game_mode = MockGameMode()

class MockBall:
    def __init__(self):
        self.x = 10
        self.y = 500
        self.vx = -1000
        self.vy = 0
        self.hp = 100
        self.alive = True
        self.radius = 15
        self.team = "test"
        self.ball_type = "test"
        self.speed = 100

def test_no_damage_in_mirror_walls():
    world = MockWorld()
    world.game_mode = MirrorWallsMode()
    ball = MockBall()
    action = Action(ball, world)

    # Run execute. Should hit the wall because x=10 and vx=-1000 and radius=15. wait, x-vx*delta?
    # No, execute runs _clamp_position and checks bounced_wall
    ball.x = -100  # this will trigger clamp and bounced_wall
    action.execute("idle", 1.0)

    assert ball.hp == 100
    assert ball.vx > 0 or hasattr(ball, "_reflection_vx")

def test_damage_in_normal_mode():
    world = MockWorld()
    ball = MockBall()
    action = Action(ball, world)

    ball.x = -100
    action.execute("idle", 1.0)

    assert ball.hp < 100

print("Testing python action logic for mirror walls")
if __name__ == "__main__":
    test_no_damage_in_mirror_walls()
    test_damage_in_normal_mode()
    print("Tests passed.")
