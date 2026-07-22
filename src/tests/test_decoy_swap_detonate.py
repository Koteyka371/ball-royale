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

def test_decoy_swap_detonate_deploy():
    w = MockWorld()
    b = MockBall(1, 100, 100, "red")
    b.skill = "decoy_swap_detonate"
    w.balls = [b]

    act = Action(b, w)
    act._use_skill()

    assert len(w.balls) == 2
    decoy = w.balls[1]
    assert decoy.is_decoy == True
    assert decoy.owner_id == 1
    assert decoy.hp == 50
    assert decoy.x == 100
    assert decoy.y == 100
    assert b.skill_timer == 5.0

def test_decoy_swap_detonate_swap_and_explode():
    w = MockWorld()
    b = MockBall(1, 100, 100, "red")
    b.skill = "decoy_swap_detonate"

    decoy = MockBall(2, 200, 200, "red")
    decoy.is_decoy = True
    decoy.owner_id = 1

    enemy = MockBall(3, 120, 120, "blue") # near decoy (distance = sqrt(20^2 + 20^2) = ~28 <= 150)
    enemy.hp = 100

    far_enemy = MockBall(4, 500, 500, "blue")
    far_enemy.hp = 100

    w.balls = [b, decoy, enemy, far_enemy]

    act = Action(b, w)
    act._use_skill()

    # Check positions
    assert b.x == 200
    assert b.y == 200

    # Decoy should be dead
    assert decoy.hp == 0
    assert decoy.alive == False

    # Explosion damage (50)
    assert enemy.hp == 50
    assert far_enemy.hp == 100

    # Event added
    assert any(e[0] == "explosion" and e[1]["x"] == 100 and e[1]["y"] == 100 for e in w.events)

def test_decoy_swap_detonate_most_recent():
    w = MockWorld()
    b = MockBall(1, 100, 100, "red")
    b.skill = "decoy_swap_detonate"

    decoy1 = MockBall(2, 200, 200, "red")
    decoy1.is_decoy = True
    decoy1.owner_id = 1

    decoy2 = MockBall(3, 300, 300, "red")
    decoy2.is_decoy = True
    decoy2.owner_id = 1

    w.balls = [b, decoy1, decoy2]

    act = Action(b, w)
    act._use_skill()

    # Most recent is decoy2 (at 300, 300)
    assert b.x == 300
    assert b.y == 300
    assert decoy2.hp == 0
    assert decoy2.alive == False
    assert decoy1.hp == 100
    assert decoy1.alive == True
