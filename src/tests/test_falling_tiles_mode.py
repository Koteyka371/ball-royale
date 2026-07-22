from ai.game_modes import GAME_MODES

class MockLeaderboardData:
    def get(self, key, default):
        return default

class MockLeaderboardManager:
    def __init__(self):
        self.data = MockLeaderboardData()

class MockWorld:
    def __init__(self):
        self.arena = type('MockArena', (), {'width': 1000, 'height': 1000})()
        self.leaderboard_manager = MockLeaderboardManager()

class MockBall:
    def __init__(self):
        self.x = 25
        self.y = 25
        self.hp = 100
        self.alive = True
        self.ball_type = "player"

def test_falling_tiles_mode_phases():
    mode = GAME_MODES['falling_tiles_royale']

    world = MockWorld()
    b1 = MockBall()

    mode.setup(world, [b1])

    assert mode.phase == "wait"
    assert mode.timer == 5.0

    # Tick until warning
    mode.tick(world, [b1], delta=5.1)
    assert mode.phase == "warning"

    # Verify falling tiles assigned correctly
    falling_tiles_len = len(mode.falling_tiles)
    assert falling_tiles_len > 0

    mode.tick(world, [b1], delta=mode.warning_duration + 0.1)
    assert mode.phase == "falling"

    # Tick past falling to create pits
    mode.tick(world, [b1], delta=mode.fall_duration + 0.1)
    assert mode.phase == "wait"
    assert len(mode.falling_tiles) == 0

    # Move ball to pit
    pit_tile = None
    for k, v in mode.tiles.items():
        if v["state"] == "pit":
            pit_tile = k
            break

    assert pit_tile is not None

    b1.x = pit_tile[0] * mode.grid_size + 1
    b1.y = pit_tile[1] * mode.grid_size + 1

    mode.tick(world, [b1], delta=0.1)
    assert b1.hp == 0.0
    assert not b1.alive
