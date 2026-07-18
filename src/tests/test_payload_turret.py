import pytest
from ai.game_modes import EscortMode, DualPayloadMode

class MockArena:
    def __init__(self):
        self.name = "basic"
        self.weather = "clear"
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, type_str, data):
        self.events.append((type_str, data))

class MockBall:
    def __init__(self, t="spectator", team="", x=0, y=0, max_hp=100.0, speed=10.0, hp=100.0):
        self.ball_type = t
        self.team = team
        self.x = x
        self.y = y
        self.alive = True
        self.hp = hp
        self.speed = speed
        self.base_speed = speed
        self.max_hp = max_hp
        self.turret_active = False

def test_escort_payload_turret():
    mode = EscortMode()
    world = MockWorld()

    # Needs to be "Defenders" for payload
    balls = [MockBall(t="normal", team="Defenders", x=100, y=500) for _ in range(4)]
    balls.append(MockBall(t="normal", team="Attackers", x=150, y=500, hp=100.0))
    mode.setup(world, balls)

    mode.payload.x = 100
    mode.payload.y = 500

    for i in range(1, 4):
        balls[i].team = "Defenders"
        balls[i].x = 110
        balls[i].y = 500

    balls[4].x = 150
    balls[4].y = 500

    mode.tick(world, balls, delta=1.0)

    assert getattr(mode.payload, "turret_active", False) == True
    assert balls[4].hp < 100
    assert balls[4].x > 150

def test_dual_payload_turret():
    mode = DualPayloadMode()
    world = MockWorld()

    balls = [MockBall(t="normal", team="Red", x=100, y=500) for _ in range(4)]
    balls.append(MockBall(t="normal", team="Blue", x=150, y=500, hp=100.0))
    mode.setup(world, balls)

    mode.payload_red.x = 100
    mode.payload_red.y = 500

    for i in range(1, 4):
        balls[i].team = "Red"
        balls[i].x = 110
        balls[i].y = 500

    balls[4].x = 150
    balls[4].y = 500

    mode.tick(world, balls, delta=1.0)

    assert getattr(mode.payload_red, "turret_active", False) == True
    assert balls[4].hp < 100
    assert balls[4].x > 150
