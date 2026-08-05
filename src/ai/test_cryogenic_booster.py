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

    def get(self, key, default=None):
        return getattr(self, key, default)

class MockBall:
    def __init__(self, team="team1", x=0, y=0):
        self.id = 1
        self.team = team
        self.x = x
        self.y = y
        self.radius = 10
        self.speed = 2
        self.used_skill_count = 0
        self.alive = True
        self.ball_type = "warrior"
        self.internal_temperature = 20.0
        self.shield_booster_active = False

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.balls = []
        self.boosters = []
        self.entities = []
        self.arena = MockArena()

    def get_nearby_entities(self, ball, radius):
        return {
            "enemies": [b for b in self.balls if b.team != ball.team],
            "allies": [],
            "boosters": self.boosters
        }

def test_collect_cryogenic_booster():
    ball = MockBall()
    enemy_near = MockBall(team="team2", x=50, y=0)
    enemy_far = MockBall(team="team2", x=300, y=0)

    booster = MockEntity(2, 0, 0, kind="cryogenic_booster")

    world = MockWorld()
    world.balls = [ball, enemy_near, enemy_far]
    world.entities = [ball, enemy_near, enemy_far]
    world.boosters = [booster]
    world.arena.hazards = [booster]

    action = Action(ball, world)
    action.execute("collect_booster", 1.0)

    # Check booster logic
    assert getattr(ball, "cryogenic_booster_timer", 0.0) == 10.0
    assert getattr(ball, "shield_booster_active", False) == True
    assert len(world.boosters) == 0

    # Evaluate action to trigger aura (decrementing timer)
    action.execute("flee", 1.0)

    # Check aura logic
    assert getattr(ball, "cryogenic_booster_timer", 0.0) == 9.0
    # Nearby enemy should be affected by aura
    assert enemy_near.internal_temperature == -30.0 # 20.0 - 50.0 * 1.0
    # Far enemy should not be affected
    assert enemy_far.internal_temperature == 20.0

if __name__ == "__main__":
    test_collect_cryogenic_booster()
    print("Test passed!")
