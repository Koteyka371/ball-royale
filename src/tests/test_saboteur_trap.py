import pytest
import math
from ai.game_modes import EscortMode

class MockArena:
    def __init__(self):
        self.hazards = []
        self.weather = ""
        self.name = "normal"

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.dead_balls = []

    def add_event(self, t, d):
        self.events.append((t, d))

class MockBall:
    def __init__(self, id, team):
        self.id = id
        self.team = team
        self.alive = True
        self.x = 0
        self.y = 0
        self.speed = 100
        self.hp = 100
        self.max_hp = 100
        self.ball_type = "normal"
        self.is_payload = False

def test_saboteur_logic():
    world = MockWorld()
    mode = EscortMode()
    payload = MockBall(1, "Defenders")
    payload.is_payload = True
    payload.ball_type = "payload"
    payload.x = 100
    payload.y = 500

    attacker = MockBall(2, "Attackers")
    attacker.x = 105
    attacker.y = 500

    defender = MockBall(3, "Defenders")
    defender.x = 200
    defender.y = 500

    balls = [payload, attacker, defender]

    mode.payload = payload

    # Tick should trigger attackers planting a trap on payload if within range
    mode.tick(world, balls, 1.0)

    # Payload should have a saboteur trap attached
    assert getattr(payload, 'has_saboteur_trap', False) == True

    # Tick for delay
    for _ in range(5):
        mode.tick(world, balls, 1.0)

    # Trap explodes, disabling abilities
    assert getattr(payload, 'abilities_disabled', False) == True
    assert getattr(payload, 'sabotaged', False) == True

    # Move attacker away so they don't plant another trap immediately after defuse
    attacker.x = 1000

    # Defender approaches to defuse (needs to follow the moving payload)
    for _ in range(6):
        defender.x = payload.x + 5
        defender.y = payload.y
        mode.tick(world, balls, 1.0)

    assert getattr(payload, 'sabotaged', False) == False
    assert getattr(payload, 'abilities_disabled', False) == False
