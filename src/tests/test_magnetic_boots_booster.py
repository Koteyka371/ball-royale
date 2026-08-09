from ai.action import Action
import math

class MockBall:
    def __init__(self, x, y, cosmetic="none"):
        self.id = 1
        self.x = x
        self.y = y
        self.vx = 100.0
        self.vy = 100.0
        self.velocity_x = 100.0
        self.velocity_y = 100.0
        self.cosmetic = cosmetic
        self.polarity_cooldown = 0
        self.alive = True
        self.team = 1
        self.hp = 100
        self.speed = 2.0
        self.skill = "dash"
        self.radius = 10.0
        self.mass = 1.0

class MockBooster:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = 5.0

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

    def clamp_position(self, x, y, radius):
        bounced = False
        new_x, new_y = x, y
        if x < radius:
            new_x = radius
            bounced = True
        elif x > self.width - radius:
            new_x = self.width - radius
            bounced = True
        if y < radius:
            new_y = radius
            bounced = True
        elif y > self.height - radius:
            new_y = self.height - radius
            bounced = True
        return new_x, new_y, bounced

class MockGameMode:
    def __init__(self, name):
        self.name = name

class MockWorld:
    def __init__(self):
        self.balls = []
        self.arena = MockArena()
        self.boosters = []
        self.items = []
        self.tick = 0
        self.game_mode = MockGameMode("Normal")

    def get_nearby_entities(self, ball, radius):
        return {"enemies": [b for b in self.balls if b != ball], "allies": []}

def test_magnetic_boots_pickup():
    ball = MockBall(500, 500)
    w = MockWorld()
    w.balls = [ball]
    booster = MockBooster(500, 500, "magnetic_boots_booster")
    w.boosters.append(booster)
    a = Action(ball, w)

    # Mocking _get_boosters and _idle to simplify collection test
    a._get_boosters = lambda: w.boosters
    a._idle = lambda d: None

    a._collect_booster(0.016)

    assert getattr(ball, "magnetic_boots_timer", 0) > 0
    assert len(w.boosters) == 0

def test_magnetic_boots_collision():
    b1 = MockBall(100, 100)
    b2 = MockBall(105, 100)  # Overlaps b1, distance 5, overlap 15
    b2.id = 2
    b2.magnetic_boots_timer = 5.0

    world = MockWorld()
    world.balls = [b1, b2]

    action_b2 = Action(b2.id, world)
    action_b2.ball = b2

    action_b2._resolve_collisions()

    # With magnetic_boots_timer active, multiplier is 0.0, so b2 should not be moved
    assert abs(b2.x - 105) < 0.01

def test_magnetic_boots_wall_bounce():
    ball = MockBall(-5, 500) # Out of bounds
    ball.magnetic_boots_timer = 5.0

    w = MockWorld()
    w.balls = [ball]
    a = Action(ball, w)

    a._clamp_position()

    # Normally velocity reflects (e.g. * 2.0). With magnetic boots, it zeroes out
    assert ball.vx == 0.0
    assert ball.vy == 100.0
    assert ball.velocity_x == 0.0
    assert ball.velocity_y == 100.0
    assert ball.x == 10.0 # Clamped to radius

def test_magnetic_boots_tick():
    ball = MockBall(500, 500)
    ball.magnetic_boots_timer = 5.0
    w = MockWorld()
    w.balls = [ball]
    a = Action(ball, w)

    # _idle calls the end of tick which applies timers
    # However we can just call the execute method roughly or simulate the end
    # We will just test the end of tick logic directly if possible.
    # Actually, timer logic is in Action.execute() end or Action.tick() equivalent.
    # Since action.execute is large, we can just call a._idle(1.0) and see if timer decreases
    # wait, timer reduction might be at the end of execute

    a.execute("idle", 1.0)
    assert ball.magnetic_boots_timer == 4.0
