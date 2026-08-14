import pytest
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 2000.0
        self.height = 2000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.alive = True
        self.radius = 20.0
        self.damage = 10.0
        self.hp = 100.0

def test_cursed_relics_mode():
    mode = GAME_MODES.get('cursed_relics')
    if not mode:
        pytest.skip("CursedRelicsMode not found")

    world = MockWorld()
    balls = [MockBall(1, 100, 100), MockBall(2, 500, 500)]

    # Test setup
    mode.setup(world, balls)

    # Check relics were spawned
    relics = [h for h in world.arena.hazards if h.kind == "cursed_relic"]
    assert len(relics) == 5

    relic = relics[0]

    # Test pickup
    relic.x = 100
    relic.y = 100
    relic.attached_id = None

    mode.tick(world, balls, 0.016)

    assert relic.attached_id == 1
    assert relic.transfer_cooldown > 0.0

    # Test buff & damage over time
    relic.transfer_cooldown = 0.0
    mode.tick(world, balls, 0.5)

    assert balls[0].damage == 20.0 # double damage
    assert balls[0].base_damage_cursed == 10.0
    assert balls[0].hp < 100.0 # hp drained
    assert relic.x == balls[0].x
    assert relic.y == balls[0].y

    # Test pass on collision
    balls[1].x = 105
    balls[1].y = 105

    mode.tick(world, balls, 0.016)

    assert relic.attached_id == 2
    assert relic.transfer_cooldown > 0.0

    # Clean up tick (b1 should lose buff, b2 shouldn't have it yet because it was just passed)
    mode.tick(world, balls, 0.016)
    assert balls[0].damage == 10.0
    assert not hasattr(balls[0], "base_damage_cursed")
    assert balls[1].damage == 20.0
