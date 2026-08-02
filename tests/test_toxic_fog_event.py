import pytest
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self):
        self.alive = True
        self.max_hp = 100.0
        self.hp = 100.0

def test_toxic_fog_event():
    mode = GAME_MODES["toxic_fog_event"]
    ball = MockBall()
    world = type('MockWorld', (), {})()

    mode.setup(world, [ball])
    assert ball._fog_base_max_hp == 100.0

    # 1. Fog is inactive initially. Tick for 19.9 seconds.
    mode.tick(world, [ball], delta=19.9)
    assert not mode.fog_active
    assert ball.max_hp == 100.0

    # 2. Tick to trigger fog
    mode.tick(world, [ball], delta=0.2)
    assert mode.fog_active
    assert mode.fog_timer > 0
    assert ball.max_hp == 70.0  # 30% reduction
    assert ball.hp == 70.0      # Current HP scaled down

    # 3. Test nullifying healing
    # If the ball somehow heals during the tick (before GameMode.tick is called),
    # the GameMode should revert the healing.
    # Simulate a heal to 80.0
    ball.hp = 80.0
    mode.tick(world, [ball], delta=0.1)
    assert ball.hp == 70.0  # Reverted to last hp (which was 70.0)

    # 4. Test taking damage
    ball.hp -= 20.0
    mode.tick(world, [ball], delta=0.1)
    assert ball.hp == 50.0  # Taking damage is fine
    assert ball._fog_last_hp == 50.0

    # 5. Test another heal attempt
    ball.hp = 60.0
    mode.tick(world, [ball], delta=0.1)
    assert ball.hp == 50.0  # Reverted back

    # 6. Tick until fog ends
    mode.tick(world, [ball], delta=10.0)
    assert not mode.fog_active
    assert ball.max_hp == 100.0
    # HP stays at 50.0
    assert ball.hp == 50.0
