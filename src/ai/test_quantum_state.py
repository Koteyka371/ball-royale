import pytest
from ai.action import Action
import math

class MockHazard:
    def __init__(self, kind, x, y, radius=20):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = radius
        self.team = "NO_TEAM"
        self.active = True

class MockArena:
    def __init__(self):
        self.hazards = [MockHazard("explosive_barrel", 10, 10)]
        self.platforms = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.events = []
    def _deal_damage(self, attacker, target):
        if getattr(target, "quantum_state_timer", 0.0) > 0:
            return
        target.hp -= attacker.damage

class MockBall:
    def __init__(self, x=0, y=0, team="A"):
        self.x = x
        self.y = y
        self.hp = 100.0
        self.stamina = 100.0
        self.skill = "quantum_state"
        self.skill_timer = 0.0
        self.speed = 2.0
        self.speed_multiplier = 1.0
        self.base_speed = 2.0
        self.team = team
        self.id = 1
        self.ball_type = "quantum"
        self.alive = True

def test_quantum_state_skill():
    world = MockWorld()
    ball = MockBall()
    enemy = MockBall(x=10, y=10, team="B")
    enemy.id = 2
    enemy.damage = 50.0
    world.balls = [ball, enemy]

    action = Action(ball, world)

    # Pre-state
    assert ball.stamina == 100.0
    assert getattr(ball, "quantum_state_timer", 0.0) == 0.0

    # Activate skill
    action._use_skill()
    assert ball.stamina == 50.0
    assert ball.quantum_state_timer == 2.0

    # Enemy tries to attack
    action_enemy = Action(enemy, world)
    action_enemy._attempt_damage(enemy, ball)

    # Immune to damage
    assert ball.hp == 100.0

    # Simulate time passing
    action.execute("idle", 2.0)

    # After 2 seconds, timer should be 0
    assert ball.quantum_state_timer == 0.0

    # Should take damage now
    action_enemy._attempt_damage(enemy, ball)
    assert ball.hp == 50.0
