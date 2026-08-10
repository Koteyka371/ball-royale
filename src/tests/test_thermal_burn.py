import pytest

def test_thermal_freeze_tag_burn():
    from ai.game_modes import ThermalFreezeTagMode

    class MockArena:
        def __init__(self):
            self.hazards = []
            self.width = 1000
            self.height = 1000

    class MockWorld:
        def __init__(self):
            self.arena = MockArena()

    class MockBall:
        def __init__(self, id, is_frozen=False):
            self.id = id
            self.alive = True
            self.ball_type = "player"
            self.x = 500
            self.y = 500
            self.radius = 10
            self.is_frozen = is_frozen
            self.hp = 100
            self.thaw_progress = 0

    mode = ThermalFreezeTagMode()
    world = MockWorld()
    ball = MockBall(1, is_frozen=True)

    class MockHazard:
        def __init__(self):
            self.id = 1
            self.x = 500
            self.y = 500
            self.radius = 100
            self.kind = "heat_zone"
            self.duration = 10

    world.arena.hazards.append(MockHazard())

    # Stay in heat zone while frozen - unfreezes after 3s
    # but does NOT take damage during those 3s, because they were frozen.
    for _ in range(300):
        mode.tick(world, [ball], 0.016)

    assert not ball.is_frozen
    assert ball.hp == 100

    # After unfreezing, staying in heat zone should cause burn damage
    # Taking fire damage if they stay for > 2s after thawing
    for _ in range(200):
        mode.tick(world, [ball], 0.016)

    assert ball.hp < 100
