import pytest
from src.ai.game_modes import BattleRoyaleMode

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 20.0
        self.alive = True
        self.ball_type = "normal"
        self.hp = 100.0
        self.team = "A"

def test_moving_obstacles():
    mode = BattleRoyaleMode()
    world = MockWorld()
    b = MockBall(500, 500)
    mode.setup(world, [b])

    # Run ticks to spawn an obstacle
    for _ in range(350): # 350 * 0.016 = 5.6 seconds > 5.0
        mode.tick(world, [b], 0.016)

    moving_walls = [h for h in world.arena.hazards if getattr(h, "kind", "") == "moving_wall"]
    assert len(moving_walls) > 0, "Moving wall should have spawned after 5 seconds"

    wall = moving_walls[0]
    initial_x, initial_y = wall.x, wall.y
    vx, vy = wall.vx, wall.vy

    # Tick again to move the wall
    mode.tick(world, [b], 0.016)
    assert wall.x != initial_x or wall.y != initial_y, "Wall should be moving based on velocity"

    # Test collision bounce
    b.x = wall.x
    b.y = wall.y
    b.vx = 100.0
    b.vy = 100.0

    mode.tick(world, [b], 0.016)

    # Because they were overlapping, ball should be bumped away and its velocity affected
    assert b.x != wall.x or b.y != wall.y, "Ball should have bounced away from wall"
