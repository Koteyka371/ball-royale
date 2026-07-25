import pytest
import sys
import copy
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

def test_manual_detonate_decoy():
    w = MockWorld()
    b = MockBall(1, 100, 100, "red")
    b.skill = "manual_detonate_decoy"

    decoy1 = MockBall(2, 200, 200, "red")
    decoy1.is_decoy = True
    decoy1.owner_id = 1

    decoy2 = MockBall(3, 300, 300, "red")
    decoy2.is_decoy = True
    decoy2.owner_id = 1

    enemy = MockBall(4, 220, 220, "blue") # near decoy1 (distance = sqrt(20^2 + 20^2) = ~28 <= 150)
    enemy.hp = 100

    far_enemy = MockBall(5, 500, 500, "blue")
    far_enemy.hp = 100

    w.balls = [b, decoy1, decoy2, enemy, far_enemy]

    act = Action(b, w)
    act._use_skill()

    # Both decoys should be dead
    assert decoy1.hp == 0
    assert decoy1.alive == False
    assert decoy2.hp == 0
    assert decoy2.alive == False

    # Explosion damage from decoy1 (50) - wait, is enemy getting hit by both?
    # Distance from enemy(220, 220) to decoy2(300, 300) = sqrt(80^2 + 80^2) = sqrt(6400 + 6400) = sqrt(12800) = 113.1
    # 113.1 <= 150.0 is True! So enemy gets hit by BOTH explosions!
    # 100 - 50 - 50 = 0.
    assert enemy.hp == 0
    assert far_enemy.hp == 100

    # Events added (two explosions)
    assert sum(1 for e in w.events if e[0] == "explosion") == 2

    # Skill on cooldown
    assert b.skill_timer == 5.0
