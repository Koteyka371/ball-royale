from ai.action import Action
from arena.procedural_arena import ProceduralArena, Hazard

class DummyBall:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.hp = 100.0
        self.alive = True

class DummyArena:
    def __init__(self):
        self.hazards = []
        self.width = 2000.0
        self.height = 2000.0
    def clamp_position(self, x, y, r=0):
        return x, y, False
    def update_zone(self, tick, delta=0):
        pass

class DummyWorld:
    def __init__(self):
        self.arena = DummyArena()
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

    assert final_dist < initial_dist


def test_gravity_well_damage():
    world = DummyWorld()
    world.arena.hazards = [
        Hazard(id=1, x=1000.0, y=1000.0, radius=200.0, kind="gravity_well", damage=10.0)
    ]

    ball = DummyBall(x=1050.0, y=1050.0, radius=10.0)
    action = Action(ball, world)

    assert ball.hp == 100.0
    action.execute("idle", 0.1)

    # 10.0 damage * 0.1 delta = 1.0
    assert ball.hp < 100.0
    print(f"HP after gravity well: {ball.hp}")

def test_gravity_well_inverted_push():
    world = DummyWorld()
    hazard = Hazard(id=1, x=1000.0, y=1000.0, radius=200.0, kind="gravity_well", damage=10.0)
    hazard.is_inverted = True
    world.arena.hazards = [hazard]

    ball = DummyBall(x=1050.0, y=1050.0, radius=10.0)
    action = Action(ball, world)

    initial_dist = ((ball.x - 1000.0)**2 + (ball.y - 1000.0)**2)**0.5
    action.execute("idle", 0.1)
    final_dist = ((ball.x - 1000.0)**2 + (ball.y - 1000.0)**2)**0.5

    print(f"Inverted Initial dist: {initial_dist}, Final dist: {final_dist}")
    assert final_dist > initial_dist
