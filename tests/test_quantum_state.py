import sys
sys.path.insert(0, 'src')
from ai.action import Action
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000
        self.height = 1000

    def clamp_position(self, x, y, r):
        return x, y, False

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.tick = 0
        self.boosters = []

    def _deal_damage(self, attacker, target):
        if hasattr(target, "take_damage"):
            target.take_damage(getattr(attacker, "damage", 10.0))

    def get_nearby_entities(self, entity, radius):
        return {"enemies": [], "allies": [], "hazards": [], "boosters": []}

class MockHazard:
    def __init__(self, kind="explosive_barrel"):
        self.kind = kind
        self.x = 50
        self.y = 50
        self.radius = 10
        self.damage = 50

class MockBall:
    def __init__(self):
        self.id = 1
        self.hp = 100.0
        self.max_hp = 100.0
        self.stamina = 100.0
        self.max_stamina = 100.0
        self.speed = 100.0
        self.base_speed = 100.0
        self.skill = "quantum_state"
        self.skill_timer = 0.0
        self.x = 50.0
        self.y = 50.0
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 10.0
        self.alive = True
        self.team = "A"
        self.damage = 10.0

    def take_damage(self, dmg):
        self.hp -= dmg

def test_quantum_state_skill_usage():
    ball = MockBall()
    world = MockWorld()
    world.balls.append(ball)

    action = Action(ball, world)

    # Use skill
    action._use_skill()

    # Should consume 50 stamina and set timer
    assert ball.stamina == 50.0
    assert getattr(ball, "quantum_state_timer", 0.0) == 3.0
    assert ball.skill_timer == getattr(ball, "SKILL_COOLDOWN", 10.0)

def test_quantum_state_dodge_damage():
    attacker = MockBall()
    attacker.id = 2
    attacker.team = "B"

    target = MockBall()
    target.quantum_state_timer = 2.0

    world = MockWorld()
    action = Action(target, world)

    action._attempt_damage(attacker, target)

    # Target should dodge because quantum_state_timer > 0
    assert target.hp == 100.0

def test_quantum_state_timer_tick():
    ball = MockBall()
    ball.quantum_state_timer = 2.0
    world = MockWorld()

    action = Action(ball, world)
    action.execute("idle", 0.5)

    assert ball.quantum_state_timer == 1.5

def test_quantum_state_hazard_pass():
    ball = MockBall()
    ball.quantum_state_timer = 2.0

    hazard = MockHazard("spikes")
    world = MockWorld()
    world.arena.hazards.append(hazard)

    action = Action(ball, world)
    action.execute("idle", 1.0)

    # Since ball is quantum, hazard shouldn't affect it
    # We can check if ball didn't take damage (spikes normally deal damage if overlapped, but it's skipped entirely)
    assert ball.hp == 100.0
