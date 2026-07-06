
from src.ai.action import Action
class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000
        self.height = 1000
    def update_zone(self, tick, delta):
        pass

class MockWorld:
    def __init__(self):
        self.balls = []
        self.arena = MockArena()
        self.tick = 1
        self.events = []
    def get_nearby_entities(self, ball, radius):
        return {"enemies": [], "allies": []}

class MockBall:
    def __init__(self, x, y, team):
        self.id = 1
        self.x = x
        self.y = y
        self.team = team
        self.ball_type = "test"
        self.hp = 100
        self.max_hp = 100
        self.damage = 10
        self.alive = True
        self.radius = 10
        self.vx = 0
        self.vy = 0
        self.attack_accuracy = 1.0
        self.skill = "energy_barrier"
        self.skill_timer = 0
        self.is_flying = False
        self.base_speed = 0
        self.speed = 0
        self.max_speed = 0
        self.friction_multiplier = 1.0
        self.stun_timer = 0
        self.pull_immune_timer = 0

class MockHazard:
    damage = 0.0
    def __init__(self, x, y, team):
        self.kind = "energy_barrier"
        self.team = team
        self.x = x
        self.y = y
        self.radius = 40

w = MockWorld()
b1 = MockBall(0, 0, "A")
w.balls = [b1]
h1 = MockHazard(20, 0, "B")
w.arena.hazards.append(h1)

a1 = Action(b1, w)
a1._process_physics = lambda dt: None
a1.execute("none", 1.0)
print(b1.x, b1.y)
