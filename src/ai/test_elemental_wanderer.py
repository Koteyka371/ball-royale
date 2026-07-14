import pytest
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, id, ball_type="normal"):
        self.id = id
        self.ball_type = ball_type
        self.alive = True
        self.x = 500.0
        self.y = 500.0
        self.radius = 20.0
        self.damage = 10.0
        self.speed = 100.0
        self.defense_multiplier = 1.0

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.dead_balls = []
        self.events = []

def test_elemental_wanderer_mode():
    mode = GAME_MODES.get("elemental_wanderer")
    assert mode is not None
    assert mode.name == "Elemental Wanderer"

    world = MockWorld()
    balls = [MockBall(1), MockBall(2)]

    # Test setup
    mode.setup(world, balls)

    # Check NPC was created
    assert hasattr(mode, "npc")
    assert mode.npc.ball_type == "elemental_wanderer_npc"
    assert mode.npc.alive == True

    # Check hazards were created
    assert len(world.arena.hazards) >= 3
    hazard_kinds = [h.kind for h in world.arena.hazards]
    assert "fire_zone" in hazard_kinds
    assert "ice_zone" in hazard_kinds
    assert "lightning_zone" in hazard_kinds

    # Test tick - basic movement
    old_x, old_y = mode.npc.x, mode.npc.y
    mode.npc.vx = 100.0
    mode.npc.vy = 0.0
    mode.tick(world, balls, delta=1.0)
    assert mode.npc.x == old_x + 100.0
    assert mode.npc.y == old_y

    # Test collision with hazard - let's forcefully move the NPC to the fire zone
    fire_h = next(h for h in world.arena.hazards if h.kind == "fire_zone")
    mode.npc.x = fire_h.x
    mode.npc.y = fire_h.y
    mode.npc.current_element = None

    initial_damage = balls[0].damage

    mode.tick(world, balls, delta=0.1)

    assert mode.npc.current_element == "fire_zone"
    assert mode.npc.element_timer > 0
    assert balls[0].damage > initial_damage

    event_types = [e["type"] for e in world.events]
    assert "elemental_npc_absorb" in event_types
    assert "buff" in event_types
