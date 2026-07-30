import math
from ai.game_modes import GameMode, ExtremeTornadoWeatherMode

def test_extreme_tornado():
    class DummyBall:
        def __init__(self, mass):
            self.mass = mass
            self.x = 500
            self.y = 500
            self.vx = 0
            self.vy = 0
            self.radius = 20
            self.alive = True

    class DummyArena:
        def __init__(self):
            self.hazards = []
            self.width = 1000
            self.height = 1000

    class DummyWorld:
        def __init__(self):
            self.arena = DummyArena()

    mode = ExtremeTornadoWeatherMode()
    world = DummyWorld()
    ball_heavy = DummyBall(mass=10)
    ball_light = DummyBall(mass=2)
    balls = [ball_heavy, ball_light]

    # Tick should spawn tornadoes
    mode.tick(world, balls, delta=1.0)
    assert len(world.arena.hazards) > 0
    tornado = world.arena.hazards[0]

    # Force balls to be inside tornado radius, and zero out velocity so it doesn't move out of radius during tick
    tornado.x = 500
    tornado.y = 500
    tornado.vx = 0
    tornado.vy = 0

    mode.tick(world, balls, delta=0.016)

    heavy_push = math.hypot(ball_heavy.vx, ball_heavy.vy)
    light_push = math.hypot(ball_light.vx, ball_light.vy)

    assert light_push > heavy_push

if __name__ == "__main__":
    test_extreme_tornado()
