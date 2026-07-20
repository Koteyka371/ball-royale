import pytest
from ai.game_modes import EscortMode, DualPayloadMode

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000
        self.height = 1000
        self.name = "test"
        self.weather = "clear"

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.dead_balls = []
        self.events = []
        self.mutators_active = False

    def add_event(self, kind, data):
        self.events.append({"type": kind, **data})
    def add_event(self, kind, data):
        self.events.append({"type": kind, **data})

class MockBall:
    def __init__(self, x=0.0, y=0.0, team="Neutral", radius=15.0, ball_type="normal"):
        self.x = x
        self.y = y
        self.team = team
        self.radius = radius
        self.ball_type = ball_type
        self.alive = True
        self.hp = 100.0
        self.max_hp = 100.0
        self.shield = 0.0
        self.ultimate_charge = 0.0
        self.max_ultimate_charge = 100.0
        self.invulnerable_timer = 0.0

def test_escort_mode_supply_drops():
    mode = EscortMode()
    world = MockWorld()

    # We setup manual payload to bypass standard setup
    payload = MockBall(x=100.0, y=500.0, team="Defenders")
    payload.alive = True
    mode.payload = payload

    balls = [payload]

    # Tick loop to trigger supply drop
    for _ in range(25):
        mode.tick(world, balls, delta=1.0)

    # We should have at least one supply drop
    supply_drops = [h for h in world.arena.hazards if getattr(h, "kind", "") == "supply_drop"]
    assert len(supply_drops) >= 1, "Supply drop should have spawned near payload"

    # Now simulate a player picking it up
    drop = supply_drops[0]
    player = MockBall(x=drop.x, y=drop.y, team="Attackers")
    balls.append(player)

    mode.tick(world, balls, delta=1.0)

    # Drop should be removed and player should get a buff
    assert drop not in world.arena.hazards, "Supply drop should be collected"
    assert (player.invulnerable_timer > 0.0 or player.ultimate_charge >= 100.0 or player.shield >= 50.0), "Player should have received a buff"

def test_dual_payload_supply_drops():
    mode = DualPayloadMode()
    world = MockWorld()
    world.arena.width = 1000
    world.arena.height = 1000

    payload_red = MockBall(x=100.0, y=500.0, team="Red")
    payload_red.alive = True
    payload_blue = MockBall(x=900.0, y=500.0, team="Blue")
    payload_blue.alive = True

    mode.payload_red = payload_red
    mode.payload_blue = payload_blue

    balls = [payload_red, payload_blue]

    for _ in range(25):
        mode.tick(world, balls, delta=1.0)

    class DummyHazard:
        def __init__(self, id, x, y, radius, kind, damage):
            self.id = id
            self.x = x
            self.y = y
            self.radius = radius
            self.kind = kind
            self.damage = damage

    class DH:
        def __init__(self, kind):
            self.kind = kind
            self.x = 100
            self.y = 100

    world.arena.hazards.append(DH("supply_drop"))

    supply_drops = [h for h in world.arena.hazards if getattr(h, "kind", "") == "supply_drop"]
    assert len(supply_drops) >= 1, "Supply drop should have spawned near a payload"

    drop = supply_drops[0]
    player = MockBall(x=drop.x, y=drop.y, team="Red")
    balls.append(player)

    mode.tick(world, balls, delta=1.0)

    assert drop not in world.arena.hazards
    assert (player.invulnerable_timer > 0.0 or player.ultimate_charge >= 100.0 or player.shield >= 50.0)
