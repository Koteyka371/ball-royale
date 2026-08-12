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
        self.skill = "blood_pact"
        self.skill_timer = 0.0
        self.lifesteal_aura_timer = 0.0

def test_blood_pact_resurrect():
    necro = MockBall(1, "red", 100, 100)
    dead_ally = MockBall(2, "red", 0, 100, "warrior")
    dead_ally.alive = False

    world = MockWorld()
    world.balls = [necro, dead_ally]

    action = Action(necro, world)
    action.execute("use_skill", 0.1)

    assert math.isclose(necro.hp, 80.0, abs_tol=1.0)
    assert dead_ally.alive == True
    assert dead_ally.hp == 100
    assert dead_ally.ball_type == "elite_minion"
    assert dead_ally.minion_owner == necro.id

def test_blood_pact_aura():
    necro = MockBall(1, "red", 100, 100)
    alive_minion = MockBall(2, "red", 100, 100, "minion")

    world = MockWorld()
    world.balls = [necro, alive_minion]

    action = Action(necro, world)
    action.execute("use_skill", 0.1)

    assert math.isclose(necro.hp, 80.0, abs_tol=1.0)
    assert alive_minion.lifesteal_aura_timer == 10.0
    assert alive_minion.lifesteal_aura_owner == necro.id
