import pytest
from ai.action import Action
class MockArena:
    def __init__(self):
        self.hazards = []
class MockWorld:
    def __init__(self, balls):
        self.arena = MockArena()
        self.balls = balls
        self.entities = balls
        self.events = []
    def add_event(self, type, data):
        self.events.append({"type": type, **data})

class MockBall:
    def __init__(self, id, x, y, team=""):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.hp = 100
        self.max_hp = 100
        self.alive = True
        self.speed = 10.0
        self.radius = 10.0
        self.skill = "delayed_decoy_swap"
        self.SKILL = "delayed_decoy_swap"
        self.skill_timer = 0.0

def test_delayed_decoy_swap():
    owner = MockBall(1, 100, 100, team="A")
    world = MockWorld([owner])
    action = Action(owner, world)

    # 1. Trigger skill to spawn decoy and set timer
    action._use_skill()
    assert len(world.balls) == 2

    decoy = world.balls[-1]
    assert decoy.is_decoy == True
    assert getattr(owner, "delayed_swap_timer", 0.0) == 3.0
    assert getattr(owner, "delayed_swap_target", None) == decoy

    # 2. Tick for 1 second, no swap yet
    action.execute("idle", 1.0)
    assert abs(owner.x - 100) < 5 and abs(owner.y - 100) < 5

    # 3. Tick for 2 more seconds, swap occurs
    # Move owner to simulate gameplay
    owner.x = 150
    owner.y = 150
    action.execute("idle", 2.01)

    assert abs(owner.x - 100) < 5 and abs(owner.y - 100) < 5 # decoy's original position
    assert abs(decoy.x - 150) < 5 and abs(decoy.y - 150) < 5
    assert getattr(owner, "delayed_swap_timer", 0.0) <= 0.0
