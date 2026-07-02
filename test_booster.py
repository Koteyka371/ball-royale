class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.boosters = []

    def get_nearby_entities(self, ball, radius):
        return {"boosters": self.boosters}

class MockBall:
    def __init__(self, team=1):
        self.team = team
        self.hp = 100
        self.x = 0
        self.y = 0
        self.id = id(self)
        self.invert_timer = 0.0

class MockHazard:
    def __init__(self, kind):
        self.kind = kind
        self.x = 0
        self.y = 0

world = MockWorld()
b1 = MockBall(1)
b2 = MockBall(2)
world.balls = [b1, b2]

booster = MockHazard("invert_booster")
world.boosters = [booster]
world.arena.hazards = [booster]

from src.ai.action import Action
action = Action(b1, world)
action.execute("collect_booster", 1/60.0)

print(b2.invert_timer)
