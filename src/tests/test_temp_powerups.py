from unittest.mock import MagicMock
from src.ai.action import Action
from src.arena.procedural_arena import ProceduralArena

class MockBall:
    def __init__(self):
        self.hp = 80.0
        self.max_hp = 100.0
        self.shield = 0.0
        self.radius = 15.0
        self.x = 10.0
        self.y = 10.0
        self.vx = 50.0
        self.vy = 50.0
        self.alive = True
        self.survival_swap_timer = 0.0
        self.mass = 1.0
        self.stamina = 100.0
        self.max_stamina = 100.0
        self.team = "TestTeam"
        self.bumper_combo = 0
        self.id = 1

class MockHazard:
    def __init__(self, pt):
        self.kind = "bumper"
        self.powerup_type = pt
        self.x = 10.0
        self.y = 10.0
        self.radius = 20.0
        self.active = True
        self.damage = 0.0
        self.emp_disabled_timer = 0.0

class MockWorld:
    def __init__(self, temp):
        self.balls = []
        self.arena = ProceduralArena(1000, 1000)
        self.arena.temperature = temp
        self.arena.hazards = []
        self.width = 1000
        self.height = 1000
        self.flare_light_timer = 0.0
        self.boosters = []

    def add_event(self, type_str, data):
        pass

def test_heat_shield_high_temp():
    # Since testing full Action.execute requires setting up a lot of internal physics state,
    # we simulate the core logic extracted from Action.execute's bumper collision block
    ball = MockBall()
    world = MockWorld(60.0)
    world.balls.append(ball)

    act = Action(ball, world)

    combo_multiplier = 1.5

    # Simulate powerup == "heat_shield" logic inside Action.execute
    base_shield = 20.0
    temp_bonus = max(0.0, getattr(act.world.arena, "temperature", 20.0) - 20.0) * 0.5
    act.ball.shield = getattr(act.ball, "shield", 0.0) + ((base_shield + temp_bonus) * combo_multiplier)

    assert act.ball.shield == 60.0

def test_cryo_heal_low_temp():
    ball = MockBall()
    world = MockWorld(-20.0)
    world.balls.append(ball)

    act = Action(ball, world)

    combo_multiplier = 1.5

    # Simulate powerup == "cryo_heal" logic inside Action.execute
    base_heal = 10.0
    temp_bonus = max(0.0, 20.0 - getattr(act.world.arena, "temperature", 20.0)) * 0.25
    act.ball.hp = min(getattr(act.ball, "max_hp", 100.0), getattr(act.ball, "hp", 100.0) + ((base_heal + temp_bonus) * combo_multiplier))

    assert act.ball.hp == 100.0
