import math
from ai.action import Action


class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 5000
        self.height = 5000
        self.safe_zone_center = (500, 500)
        self.safe_zone_radius = 5000

    def clamp_position(self, x, y, radius):
        bounced = False
        if x < radius:
            x = radius
            bounced = True
        elif x > self.width - radius:
            x = self.width - radius
            bounced = True
        if y < radius:
            y = radius
            bounced = True
        elif y > self.height - radius:
            y = self.height - radius
            bounced = True
        return x, y, bounced

class MockBooster:
    def __init__(self, kind, x, y):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = 10

class MockBall:
    def __init__(self, id, x, y, team="red"):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.team = team
        self.speed = 100.0
        self.hp = 100
        self.max_hp = 100
        self.damage = 10
        self.alive = True
        self.radius = 10

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.balls = []
        self.events = []

    def _collect_booster(self, ball, b):
        pass

def test_hologram_booster_spawns_holograms_and_they_move_fast():
    world = MockWorld()
    b = MockBooster("hologram_booster", 2500, 2500)
    world.boosters.append(b)

    ball = MockBall(1, 2500, 2500)
    world.balls.append(ball)

    action = Action(ball, world)
    action._get_boosters = lambda: [b]; action._collect_booster(1.0)

    holograms = [other for other in world.balls if getattr(other, "is_hologram", False)]
    assert len(holograms) == 1, "Should spawn 1 hologram"
    assert b not in world.boosters, "Booster should be collected"

    holo = holograms[0]
    assert holo.hp == 1.0, "Hologram HP should be 1.0"
    assert holo.damage == 0.0, "Hologram should deal 0 damage"
    assert holo.hologram_timer == 5.0, "Hologram timer should be 5.0"

    hx = holo.hologram_dir_x
    hy = holo.hologram_dir_y

    # Tick hologram to move
    # First, tick with a small delta to observe movement speed
    holo_action = Action(holo, world)
    holo_action.execute("idle", 0.016)

    speed = math.sqrt(holo.vx**2 + holo.vy**2)
    expected_speed = 1000.0
    assert abs(speed - expected_speed) < 1.0, f"Expected {expected_speed} but got {speed}"
