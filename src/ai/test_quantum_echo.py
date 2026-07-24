import pytest
import sys
sys.path.append('src')

class MockBall:
    def __init__(self, **kwargs):
        self.id = 1
        self.x = 0
        self.y = 0
        self.hp = 100
        self.alive = True
        self.traits = ["quantum_echo"]
        self.skill = "teleport"
        self.skill_timer = 0.0
        self.silence_timer = 0.0
        self.intangible = False
        self.intangible_timer = 0.0
        self.anchor_trap_timer = 0.0
        self.use_skill = lambda: None
        for k, v in kwargs.items():
            setattr(self, k, v)

class MockWorld:
    def __init__(self):
        self.balls = []
        self.events = []

from ai.action import Action

def test_quantum_echo_mechanic():
    ball = MockBall()
    world = MockWorld()
    world.balls.append(ball)

    action = Action(ball, world)

    # Tick to spawn first ghost
    action.execute("idle", 3.0)
    assert len(getattr(ball, "quantum_echo_ghosts", [])) >= 1
    assert ball.quantum_echo_ghosts[0]["hp"] == 100

    # Change state
    ball.hp = 20
    ball.x = 100
    ball.y = 100

    # Use skill to revert
    action._use_skill()

    assert ball.hp == 100
    assert ball.x == 0
    assert ball.y == 0
    assert len(ball.quantum_echo_ghosts) >= 0
