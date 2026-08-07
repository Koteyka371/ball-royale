import pytest
import sys
sys.path.append('src')
from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []
        self.boundary_states = {'top': 'wall', 'bottom': 'wall', 'left': 'wall', 'right': 'wall'}
        self.boundary_health = {'top': 100, 'bottom': 100, 'left': 100, 'right': 100}

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.boosters = []
        self.events = []
        self.next_id = 1000
        self.tick = 5

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, ball_id, x, y, team):
        self.id = ball_id
        self.x = x
        self.y = y
        self.team = team
        self.alive = True
        self.hp = 100
        self.max_hp = 100
        self.radius = 10
        self.skill = ""
        self.SKILL = ""
        self.skill_timer = 0.0
        self.SKILL_COOLDOWN = 5.0
        self.is_decoy = False
        self.decoy_type = ""
        self.decoy_timer = 0.0

def test_manual_detonate_decoy_chain():
    w = MockWorld()
    b = MockBall(1, 100, 100, "red")
    b.skill = "manual_detonate_decoy"

    decoy1 = MockBall(2, 200, 200, "red")
    decoy1.is_decoy = True
    decoy1.owner_id = 1

    decoy2 = MockBall(3, 300, 300, "red")
    decoy2.is_decoy = True
    decoy2.owner_id = 1

    decoy3 = MockBall(6, 400, 400, "red")
    decoy3.is_decoy = True
    decoy3.owner_id = 1

    enemy = MockBall(4, 220, 220, "blue")
    enemy.hp = 100

    w.balls = [b, decoy1, decoy2, decoy3, enemy]

    act = Action(b, w)
    act._use_skill()

    # The decoys should not be dead yet
    assert decoy1.hp == 100
    assert decoy1.alive == True
    assert decoy2.alive == True
    assert decoy3.alive == True

    # They should have the timer applied
    assert decoy1.decoy_type == "explosive"
    assert decoy1.decoy_timer == 3.0
    assert decoy2.decoy_type == "explosive"
    assert decoy2.decoy_timer == 3.0
    assert decoy3.decoy_type == "explosive"
    assert decoy3.decoy_timer == 3.0

    # No immediate explosion
    assert sum(1 for e in w.events if e[0] == "explosion") == 0
    assert enemy.hp == 100

    # Should create C(3, 2) = 3 laser beams
    assert len(w.arena.hazards) == 3
    for h in w.arena.hazards:
        assert h.kind == "laser_beam"
        assert h.timer == 3.0
        assert h.damage == 50.0
        assert h.team == "red"

    # Skill on cooldown
    assert b.skill_timer == 5.0
