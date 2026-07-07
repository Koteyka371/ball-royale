import pytest
import math
from ai.ball_types_entangler import Entangler
from ai.action import Action

class MockWorld:
    def __init__(self):
        self.balls = []
        self.entities = []
        self.width = 1000
        self.height = 1000
        self.events = []
        self.dead_balls = []
        self.arena = None

    def get_nearby_entities(self, entity, radius):
        return {"enemies": [], "allies": [], "boosters": [], "hazards": []}

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

def test_entangler_initialization():
    ent = Entangler(1, 100, 100)
    assert ent.hp == 120
    assert ent.SPEED == 2.5
    assert ent.DAMAGE == 10
    assert ent.SKILL == 'entangle'

def test_entangler_tether_logic():
    world = MockWorld()
    ent = Entangler(1, 100, 100)
    ent.team = "team1"
    ent.speed = 0.0 # prevent normal idle movement
    ent.base_speed = 0.0

    partner = Entangler(2, 100, 100)
    partner.team = "team2"
    partner.speed = 0.0
    partner.base_speed = 0.0

    world.balls = [ent, partner]
    world.entities = [ent, partner]

    # Manually entangle them
    ent.entangle_timer = 5.0
    ent.entangled_with_id = partner.id
    partner.entangle_timer = 5.0
    partner.entangled_with_id = ent.id

    ent.prev_hp = 120
    ent.hp = 100 # lost 20 HP
    ent.prev_x = 100
    ent.prev_y = 100

    # Move entangler
    ent.x = 120
    ent.y = 100

    action = Action(ent, world)

    # Bypass default behaviors that move the ball (e.g. friction/boids/idle jitter)
    # We just run the entangle sync loop by invoking _apply_effects explicitly
    # Actually wait, execute() runs the entanglement sync at the start.

    # Let's mock the idle logic to do nothing.
    action._idle = lambda delta: None
    action.execute("idle", 0.0)

    # Check if damage is split: 20 lost -> self recovers 10, partner loses 10
    assert math.isclose(ent.hp, 110)
    assert math.isclose(partner.hp, 110)

    # Check tether movement: ent moved +20 x -> self restored -10, partner moved +10
    assert math.isclose(ent.x, 110)
    assert math.isclose(partner.x, 110)
