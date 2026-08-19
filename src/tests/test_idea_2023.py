import sys
import math
sys.path.append('src')
from ai.game_modes import EscortMode

class MockBall:
    def __init__(self, team="Attackers"):
        self.alive = True
        self.ball_type = "player"
        self.team = team
        self.x = 100.0
        self.y = 100.0
        self.radius = 15.0
        self.hp = 100.0
        self.speed = 1.0

class MockWorld:
    def __init__(self):
        self.arena = type('MockArena', (), {'hazards': [], 'weather': ''})()
        self.events = []
    def add_event(self, kind, data):
        self.events.append((kind, data))

def test_rare_item_attackers():
    mode = EscortMode()
    world = MockWorld()

    b1 = MockBall("Defenders")
    mode.payload = b1
    mode.payload.ball_type = "payload"
    mode.payload.hp = 5000.0
    mode.payload.max_hp = 5000.0
    mode.payload.overcharge_timer = 0.0
    mode.payload.sabotaged = False

    rare_item = type('Hazard', (), {'kind': 'rare_payload_item', 'x': 100.0, 'y': 100.0, 'radius': 40.0})()
    world.arena.hazards.append(rare_item)

    b2 = MockBall("Attackers")
    b2.x = 100.0
    b2.y = 100.0

    b1.x = 1000.0
    b1.y = 1000.0

    mode.tick(world, [b1, b2], 1.0)

    assert mode.payload.hp == 3500.0
    assert len(world.events) > 0
    assert world.events[0][0] == 'payload_damaged_rare'

def test_rare_item_defenders():
    mode = EscortMode()
    world = MockWorld()

    b1 = MockBall("Defenders")
    mode.payload = b1
    mode.payload.ball_type = "payload"
    mode.payload.hp = 3000.0
    mode.payload.max_hp = 5000.0
    mode.payload.overcharge_timer = 0.0
    mode.payload.sabotaged = False

    rare_item = type('Hazard', (), {'kind': 'rare_payload_item', 'x': 100.0, 'y': 100.0, 'radius': 40.0})()
    world.arena.hazards.append(rare_item)

    b2 = MockBall("Defenders")
    b2.x = 100.0
    b2.y = 100.0

    b1.x = 1000.0
    b1.y = 1000.0

    mode.tick(world, [b1, b2], 1.0)

    assert mode.payload.hp == 4500.0
    assert mode.payload.overcharge_timer >= 5.0
    assert len(world.events) > 0
    assert any(e[0] == 'payload_healed_rare' for e in world.events)
