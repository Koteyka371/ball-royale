from ai.action import Action
import math

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.boundary_states = {}
        self.hazards = []

    def update_zone(self, tick, delta):
        pass

class MockWorld:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.arena = MockArena()
        self.game_mode = None
        self.balls = []
        self.boosters = []
        self.events = []
        self.next_id = 9999
        self.time = 0.0

    def get_nearby_entities(self, *args, **kwargs):
        return {"enemies": [], "allies": [], "boosters": []}

class MockBall(dict):
    def __init__(self, x, y, vx, vy):
        super().__init__()
        self.id = 1
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = 10.0
        self.is_projectile = False
        self.is_spell = False
        self.ball_type = "basic"
        self.intangible = False
        self.alive = True
        self.wall_stick_timer = 0.0
        self.owner_id = None
        self.duration = 10.0

        self["x"] = x
        self["y"] = y
        self["vx"] = vx
        self["vy"] = vy
        self["radius"] = 10.0

def test_wall_stick_timer_set():
    # Test that hitting the wall sets the timer and zeroes velocity
    ball = MockBall(-10.0, 500.0, -100.0, 0.0) # Outside left wall
    world = MockWorld()
    world.balls.append(ball)

    action = Action(ball, world)
    action.execute("idle", 0.1)

    assert getattr(ball, "wall_stick_timer", 0.0) > 0.0
    assert ball.vx == 0.0
    assert ball.vy == 0.0

def test_wall_stick_timer_prevents_movement():
    # Test that an existing timer prevents movement
    ball = MockBall(500.0, 500.0, 100.0, 100.0)
    ball.wall_stick_timer = 2.0
    world = MockWorld()
    world.balls.append(ball)

    action = Action(ball, world)
    action.execute("idle", 0.1)

    # Timer should decrement
    assert math.isclose(ball.wall_stick_timer, 1.9)
    # Velocity should be zeroed
    assert ball.vx == 0.0
    assert ball.vy == 0.0
    # Position should be unchanged (except for maybe idle logic, but vx/vy are 0)
    # wait, execute starts by checking timer and returning early!
    assert ball.x == 500.0
    assert ball.y == 500.0

if __name__ == "__main__":
    test_wall_stick_timer_set()
    test_wall_stick_timer_prevents_movement()
    print("All tests passed!")
