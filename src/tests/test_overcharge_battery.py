import pytest
from ai.game_modes import GameMode, DualPayloadMode

class MockBall:
    def __init__(self, x=0, y=0, team="Red", id=0):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.alive = True
        self.hp = 100
        self.max_hp = 100
        self.radius = 15.0
        self.ball_type = "normal"
        self.speed = 100.0

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

    def add_event(self, t, d):
        self.events.append((t, d))

class MockHazard:
    def __init__(self, x=0, y=0, radius=20, team="Blue"):
        self.x = x
        self.y = y
        self.radius = radius
        self.kind = "some_hazard"
        self.team = team

def test_overcharge_battery_spawns():
    mode = DualPayloadMode()
    world = MockWorld()

    payload_red = MockBall(100, 500, "Red")
    payload_red.is_payload = True
    payload_blue = MockBall(900, 500, "Blue")
    payload_blue.is_payload = True

    balls = [payload_red, payload_blue]
    mode.setup(world, balls)

    # Fast forward time to see if battery spawns
    battery_spawned = False
    for _ in range(3000): # 3000 * 0.016 = 48s, battery spawns every 25s
        mode.tick(world, balls, 0.016)
        if any(h.kind == "overcharge_battery" for h in world.arena.hazards):
            battery_spawned = True
            break

    assert battery_spawned, "Overcharge battery did not spawn"

def test_overcharge_battery_pickup_and_delivery():
    mode = DualPayloadMode()
    world = MockWorld()

    payload_red = MockBall(100, 500, "Red")
    payload_red.is_payload = True
    payload_blue = MockBall(900, 500, "Blue")
    payload_blue.is_payload = True

    player_red = MockBall(500, 500, "Red", id=1)

    balls = [payload_red, payload_blue, player_red]
    mode.setup(world, balls)
    payload_red.team = "Red"
    payload_blue.team = "Blue"
    player_red.team = "Red"

    mode.payload_red = payload_red
    mode.payload_blue = payload_blue

    class DummyBattery:
        def __init__(self):
            self.kind = "overcharge_battery"
            self.x = 500
            self.y = 500
            self.radius = 20.0

    battery = DummyBattery()
    world.arena.hazards.append(battery)

    mode.tick(world, balls, 0.016)

    assert getattr(player_red, "has_overcharge_battery", False), "Player should have picked up battery"
    assert battery not in world.arena.hazards, "Battery should be removed from arena"

    # Move player near payload
    player_red.x = 100
    player_red.y = 500

    enemy_hazard = MockHazard(team="Blue")
    world.arena.hazards.append(enemy_hazard)

    mode.tick(world, balls, 0.016)

    assert not getattr(player_red, "has_overcharge_battery", False), "Player should have delivered battery"
    assert getattr(payload_red, "is_payload_overcharged", False), "Payload should be overcharged"
    assert getattr(payload_red, "payload_overcharge_timer", 0.0) > 10.0, "Payload overcharge timer should be set"
    assert enemy_hazard not in world.arena.hazards, "Enemy structures should be destroyed"

    # Tick again to apply speed boost
    mode.tick(world, balls, 0.016)

    assert getattr(player_red, "_orig_battery_speed", None) is not None
    assert player_red.speed > 100.0, "Player speed should be boosted by 1.5x"

    # Fast forward to end of overcharge
    for _ in range(1000): # 1000 * 0.016 = 16s
        mode.tick(world, balls, 0.016)

    assert not getattr(payload_red, "is_payload_overcharged", False), "Payload should not be overcharged anymore"
    assert player_red.speed < 181.0, "Player speed should be restored"
