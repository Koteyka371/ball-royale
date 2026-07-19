import pytest
from ai.game_modes import SpectatorHologramsMode

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000.0
        self.height = 1000.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, type_str, data):
        self.events.append({"type": type_str, "data": data})

class MockBall:
    def __init__(self, id, x, y, radius=15.0, ball_type="normal"):
        self.id = id
        self.x = x
        self.y = y
        self.radius = radius
        self.ball_type = ball_type
        self.hp = 100.0
        self.alive = True
        self.speed_buff_timer = 0.0

def test_spectator_hologram_spawn():
    mode = SpectatorHologramsMode()
    world = MockWorld()

    # Fast forward to trigger spawn
    mode.apply_dynamic_traits(world, [], 11.0)

    assert len(world.arena.hazards) == 1
    hologram = world.arena.hazards[0]
    assert getattr(hologram, "kind", "") == "spectator_hologram"
    assert any(e["type"] == "hologram_spawned" for e in world.events)

def test_spectator_hologram_blocks_projectile():
    mode = SpectatorHologramsMode()
    world = MockWorld()

    class FallbackHazard:
        def __init__(self, id, x, y, radius, kind, damage):
            self.id = id
            self.x = x
            self.y = y
            self.radius = radius
            self.kind = kind
            self.damage = damage
            self.active = True
            self.duration = 20.0
            self.owner_id = None

    hologram = FallbackHazard(1, 100.0, 100.0, 30.0, "spectator_hologram", 0.0)
    world.arena.hazards.append(hologram)

    projectile = MockBall(2, 100.0, 100.0, 15.0, "projectile")
    balls = [projectile]

    mode.apply_dynamic_traits(world, balls, 0.1)

    assert projectile.hp == 0
    assert projectile.alive == False
    assert any(e["type"] == "hologram_blocked_projectile" for e in world.events)
    # Hologram should still be active
    assert hologram.active == True

def test_spectator_hologram_buffs_player():
    mode = SpectatorHologramsMode()
    world = MockWorld()

    class FallbackHazard:
        def __init__(self, id, x, y, radius, kind, damage):
            self.id = id
            self.x = x
            self.y = y
            self.radius = radius
            self.kind = kind
            self.damage = damage
            self.active = True
            self.duration = 20.0
            self.owner_id = None

    hologram = FallbackHazard(1, 100.0, 100.0, 30.0, "spectator_hologram", 0.0)
    world.arena.hazards.append(hologram)

    player = MockBall(2, 110.0, 110.0, 15.0, "normal")
    balls = [player]

    mode.apply_dynamic_traits(world, balls, 0.1)

    assert player.speed_buff_timer >= 3.0
    assert any(e["type"] == "spectator_cheer" for e in world.events)
    # Hologram should be deactivated
    assert hologram.active == False
