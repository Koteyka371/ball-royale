from ai.action import Action
import math

class MockWorld:
    def __init__(self):
        self.balls = []
        self.events = []
        self.game_mode = None

class MockBall:
    def __init__(self, id, team, hp, max_hp, ball_type="necromancer"):
        self.id = id
        self.team = team
        self.hp = hp
        self.max_hp = max_hp
        self.ball_type = ball_type
        self.alive = True
        self.x = 0
        self.y = 0
        self.skill = "dark_tether"
        self.skill_timer = 0.0
        self.dark_tether_target_id = None

def test_dark_tether_activation():
    necro = MockBall(1, "red", 100, 100)
    minion = MockBall(2, "red", 100, 100, "minion")
    minion.minion_owner = 1

    world = MockWorld()
    world.balls = [necro, minion]

    action = Action(necro, world)
    action.execute("use_skill", 0.1)

    assert necro.dark_tether_target_id == 2
