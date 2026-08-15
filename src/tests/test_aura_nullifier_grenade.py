from unittest.mock import MagicMock
from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []
    def update_zone(self, tick=0, delta=0.0):
        pass

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.events = []
    def add_event(self, type, data):
        self.events.append({"type": type, "data": data})

class MockBall:
    def __init__(self, id, x, y, team):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.speed = 100.0
        self.stamina = 100.0
        self.alive = True
        self.team = team
        self.level = 10
        self.cosmetic_aura_color = (1.0, 0.0, 0.0)
        self.reflect_shield_active = True
        self.energy_shield_active = True
        self.radius = 10.0
        self.inventory = []
        self.ball_type = 'test'
    def clamp_position(self):
        pass

def test_aura_nullifier_grenade_throw():
    world = MockWorld()
    b1 = MockBall(1, 100, 100, "team1")
    world.balls.append(b1)

    # Fake an enemy to target
    b2 = MockBall(2, 200, 100, "team2")
    world.balls.append(b2)

    action = Action(b1, world)
    action.ball.active_skill = "throw_aura_nullifier_grenade"
    action.ball.active_skill = "throw_aura_nullifier_grenade"
    action.ball.skill_timer = 0.0
    action._use_skill()

    assert len(world.arena.hazards) == 1
    hazard = world.arena.hazards[0]
    assert hazard.kind == "aura_nullifier_grenade"
    assert hazard.owner_id == 1

def test_aura_nullifier_grenade_update():
    world = MockWorld()
    b1 = MockBall(1, 100, 100, "team1")
    world.balls.append(b1)

    b2 = MockBall(2, 110, 100, "team2")
    world.balls.append(b2)

    class MockHazard:
        def __init__(self):
            self.id = "hazard1"
            self.x = 105
            self.y = 100
            self.radius = 150.0
            self.kind = "aura_nullifier_grenade"
            self.damage = 0.0
            self.duration = 5.0
            self.owner_id = 1
            self.active = True
    hazard = MockHazard()
    world.arena.hazards.append(hazard)

    action = Action(b1, world)
    action.execute("idle", 0.1)

    assert getattr(b2, "in_aura_nullifier_zone", False) == True
    assert getattr(b2, "reflect_shield_active", True) == False
    assert getattr(b2, "energy_shield_active", True) == False
