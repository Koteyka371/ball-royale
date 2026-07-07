import pytest
from ai.game_modes import MinefieldSafeZoneMode

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.dead_balls = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, x, y, alive=True, ball_type="normal"):
        self.x = x
        self.y = y
        self.alive = alive
        self.ball_type = ball_type
        self.team = ball_type
        self.hp = 100.0
        self.radius = 15.0
        self.weather_immunity_timer = 0.0

def test_minefield_safe_zone_mode():
    mode = MinefieldSafeZoneMode()
    world = MockWorld()
    balls = [MockBall(500, 500), MockBall(100, 100)]

    mode.setup(world, balls)
    assert mode.zone_radius == 500.0

    # Tick loop to trigger mine spawn
    # The first spawn should happen after base_mine_spawn_interval
    interval = mode.base_mine_spawn_interval

    # Simulate time passing
    mode.tick(world, balls, delta=interval + 0.1)

    # A mine should have been spawned
    assert len(world.arena.hazards) > 0
    mine = world.arena.hazards[0]
    assert mine.kind == "hidden_mine"
    assert mine.damage == 45.0

    # Make sure mine is spawned outside the safe zone
    # Note: distance is zone_radius + random(10, 50)
    import math
    dist = math.sqrt((mine.x - mode.zone_x)**2 + (mine.y - mode.zone_y)**2)
    assert dist > mode.zone_radius

if __name__ == '__main__':
    pytest.main(['-v', __file__])
