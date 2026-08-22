
import pytest
from ai.action import Action

class MockArena:
    def __init__(self):
        self.item_kinds = ["echolocation_booster"]
        self.safe_zone_center = (0, 0)
        self.safe_zone_radius = 5000.0

class MockWorld:
    def __init__(self):
        self.balls = []
        self.boosters = []
        self.events = []
        self.arena = MockArena()
        self.ticks = 0
    def add_event(self, event_type, data):
        self.events.append({"type": event_type, "data": data})

class MockBall:
    def __init__(self, id_val, team, x, y):
        self.id = id_val
        self.team = team
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.speed = 100.0
        self.alive = True
        self.perception_radius = 500.0
        self.stamina = 100.0
        self.max_stamina = 100.0
        self.ball_type = "default"

class MockBooster:
    def __init__(self, kind):
        self.kind = kind
        self.x = 0
        self.y = 0
        self.radius = 10.0

def test_echolocation_pulse():
    world = MockWorld()
    ball = MockBall(1, "team1", 0, 0)
    enemy1 = MockBall(2, "team2", 100, 100) # In range (radius 600)
    enemy2 = MockBall(3, "team2", 1000, 1000) # Out of range

    enemy1.invisibility_booster_timer = 10.0

    world.balls = [ball, enemy1, enemy2]

    action = Action(ball, world)

    # Collect booster manually
    ball.echolocation_booster_timer = 20.0
    ball.echolocation_pulse_timer = 0.0

    # Run execute to trigger pulse
    action.execute("aggressive", 0.1)

    # Enemy 1 should be highlighted and lose invis
    assert getattr(enemy1, "echolocation_highlight_timer", 0.0) == 3.0
    assert enemy1.invisibility_booster_timer == 0.0

    # Enemy 2 should be safe
    assert getattr(enemy2, "echolocation_highlight_timer", 0.0) == 0.0
