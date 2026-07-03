from ai.action import Action
from system.lobby import lobby

class MockBall:
    def __init__(self):
        self.id = 1
        self.hp = 100
        self.alive = True
        self.perception_radius = 250.0
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0
        self.team = "player"
        self.glitch_timer = 0.0
        self.ball_type = "basic"
        self.speed = 100
        self.base_speed = 100
        self.radius = 15.0

class MockHazard:
    def __init__(self):
        self.id = 100
        self.kind = "trap"
        self.trap_variant = "blindness"
        self.owner_id = 2
        self.x = 0
        self.y = 0
        self.radius = 15.0
        self.damage = 0.0
        self.duration = 5.0
        self.active = True

class MockArena:
    def __init__(self):
        self.hazards = [MockHazard()]
        self.width = 1000
        self.height = 1000
    def clamp_position(self, x, y, radius):
        return x, y, False
    def update_zone(self, tick, delta):
        pass

class MockWorld:
    def __init__(self):
        self.balls = []
        self.arena = MockArena()

def test_blindness_trap_perception():
    ball = MockBall()
    world = MockWorld()
    world.balls = [ball]

    action = Action(ball, world)

    # Run a tick
    action.execute("idle", 0.1)

    # Verify trap took effect
    assert getattr(ball, "is_blinded", False) == True
    assert getattr(ball, "perception_radius") == 50.0  # 250 * 0.2
    assert world.arena.hazards[0].duration == 0.0

    # Wait for effect to end (run another tick with large delta)
    action.execute("idle", 3.0)

    # Verify effect wears off
    assert getattr(ball, "is_blinded", False) == False
    assert getattr(ball, "perception_radius") == 250.0
