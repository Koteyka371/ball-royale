import pytest

class MockWall:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

class MockProjectile:
    def __init__(self, x, y, vx, vy, kind="projectile"):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.kind = kind
        self.is_projectile = True

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.projectiles = []

def test_reflective_walls_projectile_bounce():
    from src.ai.reflective_walls import ReflectiveWallsArena

    mode = ReflectiveWallsArena()
    mode.walls.append(MockWall(100, 100, 50, 200))

    world = MockWorld()
    proj = MockProjectile(99, 150, 10.0, 5.0)
    # Move projectile into the wall
    proj.x += proj.vx * 0.2
    proj.y += proj.vy * 0.2

    world.projectiles.append(proj)

    # Tick should reflect it
    mode.tick(world, [])

    assert proj.vx == -10.0
    assert proj.vy == 5.0 # y velocity should be unchanged

def test_reflective_walls_projectile_bounce_top():
    from src.ai.reflective_walls import ReflectiveWallsArena

    mode = ReflectiveWallsArena()
    mode.walls.append(MockWall(100, 100, 200, 50))

    world = MockWorld()
    proj = MockProjectile(150, 99, 5.0, 10.0)
    # Move projectile into the wall
    proj.x += proj.vx * 0.2
    proj.y += proj.vy * 0.2

    world.projectiles.append(proj)

    # Tick should reflect it
    mode.tick(world, [])

    assert proj.vx == 5.0 # x velocity should be unchanged
    assert proj.vy == -10.0
