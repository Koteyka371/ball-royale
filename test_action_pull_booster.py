from ai.action import Action

class MockWorld:
    def __init__(self):
        self.tick = 0
        self.width = 1000
        self.height = 1000
        self.arena = None
        self.boosters = []
        self.balls = []

    def get_nearby_entities(self, ball, radius):
        # Very simple nearby
        nearby = []
        for b in self.balls:
            if b != ball:
                nearby.append(b)
        return {"enemies": nearby, "allies": []}


class MockBall:
    def __init__(self):
        self.id = 1
        self.x = 500.0
        self.y = 500.0
        self.radius = 10.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.team = "A"
        self.speed = 0.0
        self.damage = 10.0
        self.base_damage = 10.0
        self._base_speed_set = True

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000
        self.height = 1000

class MockHazard:
    def __init__(self, kind):
        self.kind = kind
        self.x = 500.0
        self.y = 500.0
        self.radius = 10.0

def test_pull_booster():
    w = MockWorld()
    w.arena = MockArena()

    b = MockBall()
    w.balls.append(b)

    a = Action(b, w)

    # test it directly
    b.pull_booster_timer = 5.0

    h1 = MockHazard("spikes")
    h1.x = 600.0
    h1.y = 500.0
    h1.radius = 15.0
    w.arena.hazards.append(h1)

    h2 = MockHazard("trap")
    h2.x = 400.0
    h2.y = 500.0
    h2.radius = 20.0
    w.arena.hazards.append(h2)

    a._update_skill_timer(0.1)

    print(h1.x, h1.y)
    print(h2.x, h2.y)

test_pull_booster()
