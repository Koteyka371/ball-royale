import pytest
from src.ai.action import Action
from src.ai.ball_types_master_illusionist import MasterIllusionist

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.tick = 0
        self.next_id = 100
        self.events = []
    def add_event(self, t, d):
        pass

class MockBall:
    def __init__(self, id, x, y, team="team1", is_decoy=False, hp=100.0, alive=True):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.is_decoy = is_decoy
        self.decoy_timer = 5.0
        self.hp = hp
        self.max_hp = 100.0
        self.alive = alive
        self.speed = 2.0
        self.stutter_timer = 0.0
        self.damage = 10.0
        self.vx = 0.0
        self.vy = 0.0

def test_master_decoy_spawn():
    world = MockWorld()
    master = MasterIllusionist(1, 0, 0)
    master.team = "team1"
    master.ball_type = "master_illusionist"
    master.speed = 4.0
    master.SKILL = "master_decoy"
    master.skill_timer = 0
    master.active_skill = "master_decoy"

    world.balls.append(master)

    action = Action(master, world)

    # We can just manually call the skill
    action._use_skill()

    decoys = [b for b in world.balls if getattr(b, "is_decoy", False)]
    assert len(decoys) == 3

    types = [getattr(d, "decoy_type", "") for d in decoys]
    assert "explosive" in types
    assert "stun_trap" in types
    assert "healing_trap" in types

def test_healing_trap_explosion():
    world = MockWorld()
    decoy = MockBall(1, 0, 0, team="team1", is_decoy=True, hp=0.0)
    decoy.decoy_type = "healing_trap"

    ally1 = MockBall(2, 50, 0, team="team1", hp=20.0)
    ally2 = MockBall(3, 200, 0, team="team1", hp=20.0) # too far
    enemy = MockBall(4, 50, 0, team="team2", hp=100.0)

    world.balls = [decoy, ally1, ally2, enemy]

    action = Action(decoy, world)
    action.execute("idle", 0.1)

    assert getattr(decoy, "_decoy_exploded", False) == True
    assert ally1.hp == 60.0 # 20 + 40
    assert ally2.hp == 20.0 # Unaffected
    assert enemy.hp == 100.0 # Unaffected
