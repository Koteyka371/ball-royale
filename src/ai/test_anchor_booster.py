import sys
import os
sys.path.insert(0, os.path.abspath('src'))
from ai.action import Action

class MockEntity:
    def __init__(self, id, x, y, kind=None):
        self.id = id
        self.x = x
        self.y = y
        self.kind = kind
        self.ball_type = "booster"

class MockBall:
    def __init__(self, team="team1"):
        self.id = 1
        self.team = team
        self.x = 0
        self.y = 0
        self.radius = 10
        self.speed = 2
        self.alive = True
        self.ball_type = "warrior"
        self.base_speed = 10
        self.hp = 100
        self.stamina = 100
        self.anchor_booster_timer = 0.0

class MockWorld:
    def __init__(self):
        self.balls = []
        self.boosters = []
        self.entities = []
        self.arena = type('MockArena', (), {'hazards': [], 'wind_dx': 100.0, 'wind_dy': 100.0})()

    def get_nearby_entities(self, ball, radius):
        return {
            "enemies": [],
            "allies": [],
            "boosters": self.boosters
        }

def test_anchor_booster():
    ball = MockBall()
    booster = MockEntity(2, 0, 0, kind="anchor_booster")

    world = MockWorld()
    world.balls = [ball]
    world.entities = [ball]
    world.boosters = [booster]
    world.arena.hazards = [booster]

    action = Action(ball, world)
    action.execute("collect_booster", 1.0)

    assert ball.anchor_booster_timer > 0.0
    assert len(world.arena.hazards) == 0
    assert len(world.boosters) == 0

    # Test wind
    ball.x = 0
    ball.y = 0
    action.execute("idle", 0.1)

    # Gravity well
    gw = type('MockHazard', (), {'id': 99, 'x': 100, 'y': 0, 'kind': 'gravity_well', 'radius': 500, 'damage': 0.0})()
    world.arena.hazards.append(gw)

    ball.x = 0
    ball.y = 0
    action.execute("idle", 0.1)

    print("Test passed!")

if __name__ == "__main__":
    test_anchor_booster()
