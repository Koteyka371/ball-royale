from ai.action import Action
from arena.procedural_arena import ProceduralArena, Hazard

class DummyBall:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.hp = 100.0
        self.alive = True
        self.anchor_booster_timer = 0.0

class DummyWorld:
    def __init__(self):
        self.arena = ProceduralArena(2000.0, 0)
        self.tick = 0
        self.boosters = []

world = DummyWorld()
world.arena.hazards = [
    Hazard(id=1, x=1000.0, y=1000.0, radius=200.0, kind="gravity_well", damage=0.0)
]

ball = DummyBall(x=1000.0, y=1000.0, radius=10.0)
action = Action(ball, world)

action.execute("idle", 0.1)
print(ball.x, ball.y)
