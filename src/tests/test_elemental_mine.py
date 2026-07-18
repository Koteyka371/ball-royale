import pytest
import math
from arena.procedural_arena import ProceduralArena
from ai.action import Action

class MockWorld:
    def __init__(self):
        # Prevent generation logic to avoid TypeError and unwanted physics
        self.arena = ProceduralArena(2000, 2000)
        self.arena.hazards = []
        self.arena.rooms = []
        self.arena.corridors = []

class MockBall:
    def __init__(self):
        self.id = 1
        self.x = 100.0
        self.y = 100.0
        self.radius = 10.0
        self.hp = 100.0
        self.alive = True
        self.vx = 0.0
        self.vy = 0.0

class MockHazard:
    def __init__(self, kind="trap", trap_variant="elemental_mine"):
        self.id = 999
        self.kind = kind
        self.trap_variant = trap_variant
        self.x = 100.0
        self.y = 100.0
        self.radius = 20.0
        self.active = True
        self.duration = 10.0

def test_elemental_mine_player_collision():
    world = MockWorld()
    ball = MockBall()
    action = Action(ball, world)

    mine = MockHazard()
    world.arena.hazards.append(mine)

    # Run the collision logic in Action
    # This involves setting up the state so that the trap triggers
    # Actually, the action execute handles this when processing hazards.
    # It loops over self.world.arena.hazards.
    action.execute("idle", 0.1)

    # Check that mine was deactivated and a new hazard spawned
    assert mine.duration == 0.0
    # There should be at least 2 hazards now (mine deactivated, and the new fire/poison hazard).
    # Since action.execute can spawn multiple things, check that our new hazard exists.
    assert len(world.arena.hazards) >= 2

    # Verify we added the right hazard
    new_hazards = [h for h in world.arena.hazards if getattr(h, "kind", "") in ["fire_zone", "poison_cloud"]]
    assert len(new_hazards) >= 1
    new_hazard = new_hazards[-1]
    assert new_hazard.radius == 80.0

def test_elemental_mine_tornado_collision():
    # Pass integers to avoid TypeError during generation in ProceduralArena
    arena = ProceduralArena(2000, 2000)
    arena.hazards = []
    arena.rooms = []
    arena.corridors = []

    mine = MockHazard(kind="trap", trap_variant="elemental_mine")
    mine.id = 1
    arena.hazards.append(mine)

    tornado = MockHazard(kind="tornado", trap_variant="")
    tornado.id = 2
    # ensure it's close enough to collide
    tornado.x = 100.0
    tornado.y = 100.0
    arena.hazards.append(tornado)

    arena.update_zone(1, 0.1)

    # Check that mine was deactivated
    assert mine.active == False
    assert mine.duration == 0.0

    # Check that tornado transformed and explosion spawned
    assert tornado.kind in ["firenado", "poison_tornado"]
    # There should be at least 2 hazards now (tornado transformed and explosion spawned).
    # If the mine was removed, it might be fewer than 3, so check based on type instead.
    explosions = [h for h in arena.hazards if getattr(h, "kind", "") in ["fire_zone", "poison_cloud"]]
    assert len(explosions) >= 1
    explosion = explosions[-1]
    assert explosion.radius == 150.0
