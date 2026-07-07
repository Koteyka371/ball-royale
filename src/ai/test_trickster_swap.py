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

class MockBall:
    def __init__(self, id, x, y, team=""):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.hp = 100
        self.max_hp = 100
        self.alive = True
        self.stun_timer = 0.0
        self.burn_timer = 0.0
        self.poison_timer = 0.0
        self.confusion_timer = 0.0
        self.skill_timer = 0.0
        self.is_stunned = False
        self.skill = "trickster_swap"
        self.SKILL_COOLDOWN = 4.0

def test_trickster_swap():
    trickster = MockBall(1, 100.0, 100.0, team="A")
    trickster.burn_timer = 5.0
    trickster.poison_timer = 3.0

    target = MockBall(2, 200.0, 200.0, team="B")

    world = MockWorld([trickster, target])
    action = Action(trickster, world)

    # Run skill
    action._use_skill()

    # Check positions swapped
    assert trickster.x == 200.0
    assert trickster.y == 200.0
    assert target.x == 100.0
    assert target.y == 100.0

    # Check statuses transferred
    assert trickster.burn_timer == 0.0
    assert trickster.poison_timer == 0.0
    assert target.burn_timer == 5.0
    assert target.poison_timer == 3.0

    # Check confusion applied
    assert target.confusion_timer >= 3.0


def test_trickster_swap_with_decoy():
    trickster = MockBall(1, 100.0, 100.0, team="A")
    trickster.burn_timer = 5.0

    # Close enemy
    target = MockBall(2, 150.0, 150.0, team="B")

    # Far decoy owned by trickster
    decoy = MockBall(3, 300.0, 300.0, team="A")
    decoy.is_decoy = True
    decoy.owner_id = trickster.id

    world = MockWorld([trickster, target, decoy])
    action = Action(trickster, world)

    # Run skill
    action._use_skill()

    # Trickster should swap with the decoy, which is furthest, not the closer target
    assert trickster.x == 300.0
    assert trickster.y == 300.0
    assert decoy.x == 100.0
    assert decoy.y == 100.0

    # Target enemy shouldn't move
    assert target.x == 150.0
    assert target.y == 150.0

    # Statuses transferred to decoy
    assert trickster.burn_timer == 0.0
    assert decoy.burn_timer == 5.0
    assert decoy.confusion_timer >= 3.0
