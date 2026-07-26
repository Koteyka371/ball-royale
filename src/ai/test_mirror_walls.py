import pytest
from ai.action import Action
from ai.game_modes import MirrorWallsMode

class MockGameMode:
    def __init__(self, name="Normal"):
        self.name = name

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self, width=1000, height=1000):
        self.width = width
        self.height = height
        self.arena = MockArena()
        self.game_mode = MockGameMode()
        self.projectiles = []

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

class MockProjectile:
    def __init__(self, x, y, vx, vy, radius=5, hp=1, alive=True, ball_type="projectile"):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.hp = hp
        self.alive = alive
        self.ball_type = ball_type

def test_no_damage_in_mirror_walls():
    world = MockWorld()
    world.game_mode = MirrorWallsMode()
    ball = MockBall()
    action = Action(ball, world)
    ball.x = -100
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

def test_mirror_walls_reflect_projectiles():
    mode = MirrorWallsMode()
    world = MockWorld()
    proj1 = MockProjectile(1, 100, -100, 0)
    world.projectiles.append(proj1)
    mode.tick(world, [], 0.016)
    assert proj1.vx == 100

if __name__ == "__main__":
    test_no_damage_in_mirror_walls()
    test_damage_in_normal_mode()
    test_mirror_walls_reflect_projectiles()
    print("Tests passed.")
