import pytest
from ai.action import Action

class MockBall:
    def __init__(self, x=0, y=0, ball_type="warrior", id=1):
        self.x = x
        self.y = y
        self.ball_type = ball_type
        self.id = id
        self.alive = True
        self.hp = 100
        self.speed = 2.0
        self.radius = 10.0
        self.perception_radius = 250.0
        self.is_frictionless = False
        self.is_silenced = False
        self.silencer_timer = 0.0
        self.extended_mag_timer = 0.0
        self.modified_scope_timer = 0.0
        self.base_perception_radius = 250.0

class MockEntity:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.active = True

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.balls = []
        self.boosters = []
        self.arena = MockArena()
        self.events = []
        self.time = 0.0

def test_silencer_attachment():
    world = MockWorld()
    ball = MockBall(0, 0)
    world.balls.append(ball)

    silencer = MockEntity(10, 10, "silencer_attachment")
    world.boosters.append(silencer)
    world.arena.hazards.append(silencer)

    act = Action(ball, world)
    act.execute("collect_booster", 1.0)

    assert ball.silencer_timer > 0.0
    assert ball.is_silenced == True
    assert len(world.boosters) == 0

def test_extended_mag_attachment():
    world = MockWorld()
    ball = MockBall(0, 0)
    world.balls.append(ball)

    ext_mag = MockEntity(10, 10, "extended_mag_attachment")
    world.boosters.append(ext_mag)
    world.arena.hazards.append(ext_mag)

    act = Action(ball, world)
    act.execute("collect_booster", 1.0)

    assert ball.extended_mag_timer > 0.0
    assert len(world.boosters) == 0

def test_modified_scope_attachment():
    world = MockWorld()
    ball = MockBall(0, 0)
    world.balls.append(ball)

    mod_scope = MockEntity(10, 10, "modified_scope_attachment")
    world.boosters.append(mod_scope)
    world.arena.hazards.append(mod_scope)

    act = Action(ball, world)
    act.execute("collect_booster", 1.0)

    assert ball.modified_scope_timer > 0.0
    assert ball.perception_radius > 250.0
    assert len(world.boosters) == 0

if __name__ == "__main__":
    test_silencer_attachment()
    test_extended_mag_attachment()
    test_modified_scope_attachment()
    print("Tests pass!")
