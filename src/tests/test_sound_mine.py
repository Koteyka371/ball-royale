import math
from ai.action import Action

class MockBall:
    def __init__(self, id, x, y, skill):
        self.id = id
        self.x = x
        self.y = y
        self.hp = 100
        self.ball_type = "basic"
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 10.0
        self.suspended_projectiles = []
        self.state_history = []
        self.last_teleport_tick = -100
        self.skill = skill
        self.skill_timer = 0.0
    def use_skill(self):
        pass

class MockWorld:
    def __init__(self):
        self.next_id = 9999
        self.hazards = []
        self.balls = []
        self.events = []
        self.arena = type("Arena", (), {"hazards": self.hazards})()
    def _deal_damage(self, att, victim, dmg=None):
        if dmg is not None:
            victim.hp -= dmg
    def get_nearby_entities(self, ball, radius):
        return {"enemies": [], "boosters": [], "traps": []}

class MockHazard:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = 100.0
        self.duration = 10.0
        self.active = True

def test_sound_mine_triggers_on_noisy_skill():
    ball = MockBall(1, 50, 50, "dash")
    world = MockWorld()
    world.balls.append(ball)
    mine = MockHazard(50, 50, "sound_mine")
    world.arena.hazards.append(mine)

    action = Action(ball, world)
    action.execute('use_skill', 0.1)

    assert mine.duration == 0.0
    assert mine.active == False
    assert ball.hp < 100 # Took damage

def test_sound_mine_ignores_silent_skill():
    ball = MockBall(1, 50, 50, "energy_shield")
    world = MockWorld()
    world.balls.append(ball)
    mine = MockHazard(50, 50, "sound_mine")
    world.arena.hazards.append(mine)

    action = Action(ball, world)
    action.execute('use_skill', 0.1)

    assert mine.duration > 0.0
    assert mine.active == True
    assert ball.hp == 100
