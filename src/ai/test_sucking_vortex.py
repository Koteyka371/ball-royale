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
        self.balls = []

def test_sucking_vortex_pull():
    world = DummyWorld()
    world.arena.hazards = [
        Hazard(id=1, x=1000.0, y=1000.0, radius=200.0, kind="sucking_vortex", damage=20.0)
    ]

    ball = DummyBall(x=1050.0, y=1050.0, radius=10.0)
    world.balls.append(ball)
    action = Action(ball, world)

    initial_dist = ((ball.x - 1000.0)**2 + (ball.y - 1000.0)**2)**0.5
    action.execute("idle", 0.1)
    final_dist = ((ball.x - 1000.0)**2 + (ball.y - 1000.0)**2)**0.5

    assert final_dist < initial_dist

def test_sucking_vortex_damage():
    world = DummyWorld()
    world.arena.hazards = [
        Hazard(id=1, x=1000.0, y=1000.0, radius=200.0, kind="sucking_vortex", damage=20.0)
    ]

    # Place ball right in the center to take damage
    ball = DummyBall(x=1000.0, y=1000.0, radius=10.0)
    world.balls.append(ball)
    action = Action(ball, world)

    assert ball.hp == 100.0
    action.execute("idle", 0.1)

    # It should take 2.0 damage
    assert ball.hp < 100.0
