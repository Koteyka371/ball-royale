import pytest
from ai.action import Action

class MockWorld:
    def __init__(self, balls):
        self.balls = balls
        self.events = []
        self.next_id = 1000

    def add_event(self, type, data):
        self.events.append({"type": type, "data": data})

class MockBall:
    def __init__(self, id, x, y, team=""):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.hp = 100
        self.max_hp = 100
        self.alive = True
        self.skill = "decoy_swap_detonate"
        self.SKILL = "decoy_swap_detonate"
        self.speed = 10.0
        self.skill_timer = 0.0

    def take_damage(self, dmg, source=None):
        self.hp -= dmg

def test_decoy_swap_detonate_place_decoy():
    owner = MockBall(1, 100, 100, team="A")
    world = MockWorld([owner])
    action = Action(owner, world)

    action._use_skill()

    assert len(world.balls) == 2
    decoy = world.balls[-1]
    assert decoy.is_decoy is True
    assert decoy.owner_id == owner.id
    assert decoy.x == 100
    assert decoy.y == 100

def test_decoy_swap_detonate_swap_and_explode():
    owner = MockBall(1, 100, 100, team="A")

    decoy = MockBall(2, 200, 200, team="A")
    decoy.is_decoy = True
    decoy.owner_id = owner.id
    decoy.decoy_type = "basic"

    # Enemy is close to where the owner WAS (the new position of the decoy)
    enemy1 = MockBall(3, 110, 110, team="B")

    # Enemy is close to where the decoy WAS (the new position of the owner)
    enemy2 = MockBall(4, 210, 210, team="B")

    world = MockWorld([owner, decoy, enemy1, enemy2])
    action = Action(owner, world)

    action._use_skill()

    assert owner.x == 200
    assert owner.y == 200

    assert decoy.hp == 0
    assert decoy.alive is False

    # The code currently explores around tx, ty (which is the original owner position, 100, 100)
    assert enemy1.hp == 50
    assert enemy2.hp == 100
