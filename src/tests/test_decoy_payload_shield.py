import sys
import os
import pytest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from ai.game_modes import EscortMode

class MockBall:
    def __init__(self, id, team, x, y):
        self.id = id
        self.team = team
        self.x = x
        self.y = y
        self.alive = True
        self.hp = 100.0
        self.max_hp = 100.0
        self.ball_type = "normal"
        self.shield = 0.0
        self.max_shield = 50.0

class MockWorld:
    def __init__(self):
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

def test_decoy_payload_shield_only():
    mode = EscortMode()
    world = MockWorld()

    mode.decoy_timer = 15.0
    mode.payload = MockBall(1, "Defenders", 5000, 5000)

    balls = [mode.payload]
    mode.tick(world, balls, 0.1)

    assert mode.decoy_deployed is True

    mode.decoy.x = 100
    mode.decoy.y = 100

    defender = MockBall(2, "Defenders", 110, 100) # Near decoy
    attacker = MockBall(3, "Attackers", 110, 100) # Near decoy
    far_defender = MockBall(4, "Defenders", 900, 900) # Far from both decoy and payload

    balls = [mode.payload, mode.decoy, defender, attacker, far_defender]

    for b in balls:
        if hasattr(b, "shield"):
            b.shield = 0.0

    mode.tick(world, balls, 0.1)

    assert defender.shield > 0.0
    assert attacker.shield == 0.0
    assert far_defender.shield == 0.0

if __name__ == '__main__':
    pytest.main([__file__])
