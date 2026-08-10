from unittest.mock import MagicMock
from ai.game_modes import StickyBoundariesMode

class TestStickyBoundariesMode:
    def test_sticky_boundaries_left_wall(self):
        mode = StickyBoundariesMode()
        world = MagicMock()
        world.arena.width = 1000.0
        world.arena.height = 1000.0

        class DummyBall:
            def __init__(self, id, x, y, radius, vx, vy):
                self.id = id
                self.x = x
                self.y = y
                self.radius = radius
                self.vx = vx
                self.vy = vy
                self.alive = True
                self.ball_type = 'player'
                self.slime_immunity_timer = 0.0
                self.slime_stuck_timer = 0.0

        # Ball moving left, hitting boundary
        ball = DummyBall(1, 10.0, 500.0, 15.0, -100.0, 0.0)

        # Tick 1: Ball hits boundary
        mode.tick(world, [ball], 0.1)

        assert ball.slime_stuck_timer == 3.0
        assert ball.vx == 0.0
        assert ball.vy == 0.0
        assert ball.x == 15.0

        # Tick 2: Ball is stuck, cannot move
        ball.vx = 50.0  # Try to move
        mode.tick(world, [ball], 0.1)

        assert ball.slime_stuck_timer == 2.9
        assert ball.vx == 0.0
        assert ball.vy == 0.0

        # Fast forward time to when unstuck
        mode.tick(world, [ball], 2.9)
        assert ball.slime_stuck_timer == 0.0
        assert ball.slime_immunity_timer == 0.5

        # Tick 3: Ball has immunity, can move without getting restuck
        ball.x = 10.0
        ball.vx = -100.0
        mode.tick(world, [ball], 0.1)

        assert ball.slime_immunity_timer == 0.4
        assert ball.slime_stuck_timer == 0.0
        assert ball.vx == -100.0

    def test_sticky_boundaries_right_wall(self):
        mode = StickyBoundariesMode()
        world = MagicMock()
        world.arena.width = 1000.0
        world.arena.height = 1000.0

        class DummyBall:
            def __init__(self, id, x, y, radius, vx, vy):
                self.id = id
                self.x = x
                self.y = y
                self.radius = radius
                self.vx = vx
                self.vy = vy
                self.alive = True
                self.ball_type = 'player'
                self.slime_immunity_timer = 0.0
                self.slime_stuck_timer = 0.0

        # Ball moving right, hitting boundary
        ball = DummyBall(1, 990.0, 500.0, 15.0, 100.0, 0.0)

        # Tick 1: Ball hits boundary
        mode.tick(world, [ball], 0.1)

        assert ball.slime_stuck_timer == 3.0
        assert ball.vx == 0.0
        assert ball.vy == 0.0
        assert ball.x == 1000.0 - 15.0

    def test_sticky_boundaries_top_wall(self):
        mode = StickyBoundariesMode()
        world = MagicMock()
        world.arena.width = 1000.0
        world.arena.height = 1000.0

        class DummyBall:
            def __init__(self, id, x, y, radius, vx, vy):
                self.id = id
                self.x = x
                self.y = y
                self.radius = radius
                self.vx = vx
                self.vy = vy
                self.alive = True
                self.ball_type = 'player'
                self.slime_immunity_timer = 0.0
                self.slime_stuck_timer = 0.0

        # Ball moving up, hitting boundary
        ball = DummyBall(1, 500.0, 10.0, 15.0, 0.0, -100.0)

        # Tick 1: Ball hits boundary
        mode.tick(world, [ball], 0.1)

        assert ball.slime_stuck_timer == 3.0
        assert ball.vx == 0.0
        assert ball.vy == 0.0
        assert ball.y == 15.0

    def test_sticky_boundaries_bottom_wall(self):
        mode = StickyBoundariesMode()
        world = MagicMock()
        world.arena.width = 1000.0
        world.arena.height = 1000.0

        class DummyBall:
            def __init__(self, id, x, y, radius, vx, vy):
                self.id = id
                self.x = x
                self.y = y
                self.radius = radius
                self.vx = vx
                self.vy = vy
                self.alive = True
                self.ball_type = 'player'
                self.slime_immunity_timer = 0.0
                self.slime_stuck_timer = 0.0

        # Ball moving down, hitting boundary
        ball = DummyBall(1, 500.0, 990.0, 15.0, 0.0, 100.0)

        # Tick 1: Ball hits boundary
        mode.tick(world, [ball], 0.1)

        assert ball.slime_stuck_timer == 3.0
        assert ball.vx == 0.0
        assert ball.vy == 0.0
        assert ball.y == 1000.0 - 15.0
