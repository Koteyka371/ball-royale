import pytest
import math
from ai.action import Action

class MockBall:
    def __init__(self, x, y, radius=10.0, scale=1.0):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.radius = radius
        self.scale = scale
        self.hp = 100
        self.alive = True
        self.id = id(self)
        self.silence_timer = 0.0
        self.team = 1

class MockWorld:
    def __init__(self):
        self.entities = []
        self.events = []

    def get_nearby_entities(self, entity, radius):
        # Depending on what action.py calls, `entity` might be a Ball or a dict.
        ex = getattr(entity, 'x', entity.get('x', 0.0) if isinstance(entity, dict) else 0.0)
        ey = getattr(entity, 'y', entity.get('y', 0.0) if isinstance(entity, dict) else 0.0)
        return {"enemies": [e for e in self.entities if e != entity], "allies": [], "hazards": []}

    def add_event(self, event_type, payload):
        self.events.append({"type": event_type, "payload": payload})

def test_aura_clash_shockwave():
    world = MockWorld()
    b1 = MockBall(0, 0, scale=2.0)
    b2 = MockBall(10, 0, scale=2.0)
    b3 = MockBall(50, 0, scale=1.0) # Within 300

    world.entities = [b1, b2, b3]

    action = Action(b1, world)
    action._resolve_collisions()

    # Assert events were generated
    explosion_events = [e for e in world.events if e["type"] == "explosion" and e["payload"]["radius"] == 300.0]
    audio_events = [e for e in world.events if e["type"] == "audio_event" and e["payload"]["type"] == "aura_clash"]

    assert len(explosion_events) > 0, "Explosion event was not created"
    assert len(audio_events) > 0, "Audio event was not created"

    # Assert silence applied to nearby entity
    assert getattr(b3, "silence_timer", 0.0) == 2.0, "Nearby entity was not silenced"
    assert getattr(b3, "vx", 0.0) > 0.0, "Nearby entity was not knocked back"

def test_aura_clash_shockwave_not_triggered_low_scale():
    world = MockWorld()
    b1 = MockBall(0, 0, scale=1.9)
    b2 = MockBall(10, 0, scale=2.0)
    b3 = MockBall(50, 0, scale=1.0) # Within 300

    world.entities = [b1, b2, b3]

    action = Action(b1, world)
    action._resolve_collisions()

    # Assert events were NOT generated
    explosion_events = [e for e in world.events if e["type"] == "explosion" and e["payload"]["radius"] == 300.0]
    audio_events = [e for e in world.events if e["type"] == "audio_event" and e["payload"]["type"] == "aura_clash"]

    assert len(explosion_events) == 0, "Explosion event was created incorrectly"
    assert len(audio_events) == 0, "Audio event was created incorrectly"

    # Assert silence NOT applied to nearby entity
    assert getattr(b3, "silence_timer", 0.0) == 0.0, "Nearby entity was silenced incorrectly"
    assert getattr(b3, "vx", 0.0) == 0.0, "Nearby entity was knocked back incorrectly"
