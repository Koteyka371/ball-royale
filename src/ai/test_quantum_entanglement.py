from unittest.mock import MagicMock
from ai.action import Action

class MockBall:
    def __init__(self, id, team=0):
        self.id = id
        self.team = team
        self.x = 0.0
        self.y = 0.0
        self.y = 0
        self.hp = 100
        self.stamina = 100
        self.speed_multiplier = 1.0
        self.stamina_regen_multiplier = 1.0
        self.skill = "quantum_entanglement"
        self.alive = True
        self.skill_timer = 0
        self.quantum_prev_hp = 100
        self.quantum_entangled_target = None
        self.siren_feared_timer = 0
        self.radius = 10.0
        self.ball_type = "normal"
        self.is_ghost = False
        self.aura_booster_timer = 0.0
        self.aura_disruption_timer = 0.0

def test_quantum_link():
    world = MagicMock()
    world.arena = MagicMock()
    world.arena.safe_zone_center = (0, 0)
    world.arena.safe_zone_radius = 1000.0
    world.arena.clamp_position = MagicMock(return_value=(0, 0, False))
    ball1 = MockBall(1)
    ball2 = MockBall(2)
    ball2.x = 100
    world.balls = [ball1, ball2]

    action = Action(ball1, world)
    action._apply_friendly_aura = MagicMock()
    action._use_skill()
    assert ball1.quantum_entangled_target == 2
    assert ball2.quantum_entangled_target == 1

    action.execute("idle", 0.1)
    action2 = Action(ball2, world)
    action2._apply_friendly_aura = MagicMock()
    action2.execute("idle", 0.1)

    assert ball1.speed_multiplier == 1.5
    assert ball1.stamina_regen_multiplier == 2.0

    ball1.hp -= 20
    action.execute("idle", 0.1)
    # The damage should be mitigated
    assert ball1.hp == 90
    assert ball2.hp == 90

    # Ensure no recursive damage logic is triggered on ball2 tick
    action2.execute("idle", 0.1)
    assert ball1.hp == 90
    assert ball2.hp == 90
