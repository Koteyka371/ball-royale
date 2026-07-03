from ai.action import Action
from arena.procedural_arena import ProceduralArena, Hazard

class DummyBall:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.hp = 100.0
        self.alive = True

class DummyWorld:
    def __init__(self):
        self.arena = ProceduralArena(2000.0, 0)
        self.tick = 0
        self.boosters = []

def test_gravity_well_pull():
    world = DummyWorld()
    world.arena.hazards = [
        Hazard(id=1, x=1000.0, y=1000.0, radius=200.0, kind="gravity_well", damage=0.0)
    ]

    ball = DummyBall(x=1050.0, y=1050.0, radius=10.0)
    action = Action(ball, world)

    initial_dist = ((ball.x - 1000.0)**2 + (ball.y - 1000.0)**2)**0.5
    print(f"Initial: x={ball.x}, y={ball.y}, dist={initial_dist}")

    action.execute("idle", 0.1)

    final_dist = ((ball.x - 1000.0)**2 + (ball.y - 1000.0)**2)**0.5
    print(f"Final: x={ball.x}, y={ball.y}, dist={final_dist}")

test_gravity_well_pull()
