import pytest
from system.guild import GuildManager
from ai.game_modes import GAME_MODES
from unittest.mock import MagicMock

class MockBall:
    def __init__(self, bid, x, y):
        self.id = bid
        self.x = x
        self.y = y
        self.hp = 100

def test_guild_obstacle_course():
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as f:
        gm = GuildManager(f.name)

    gm.create_guild("ObstacleGuild", "p1")
    gm.data["guilds"]["ObstacleGuild"]["resources"] = 5000
    gm.save()

    gm.build_hq_defense("ObstacleGuild", "turret", 100, 1)
    gm.arrange_hq_item("ObstacleGuild", "defenses", "turret", 500.0, 500.0)

    gm.unlock_hq_feature("ObstacleGuild", "mini_games", "obstacle_course", 100)

    mode = GAME_MODES.get("guild_obstacle_course")
    assert mode is not None

    world = MagicMock()
    world.arena = MagicMock()
    world.arena.width = 2000.0
    world.arena.height = 2000.0
    world.arena.hazards = []

    world.guild_manager = gm
    world.active_guild_name = "ObstacleGuild"

    # Mock leaderboard manager to avoid KeyError with mock
    world.leaderboard_manager = MagicMock()
    world.leaderboard_manager.data = {"current_season": 1}

    b1 = MockBall(1, 0, 0)
    b2 = MockBall(2, 0, 0)

    mode.setup(world, [b1, b2])

    # Should spawn at start
    assert b1.x == 100.0
    assert b1.y == 100.0

    # Hazard should be spawned
    assert len(world.arena.hazards) == 1
    assert world.arena.hazards[0].x == 500.0
    assert world.arena.hazards[0].y == 500.0

    # Tick simulation
    mode.tick(world, [b1, b2], 1.0)

    # b1 stays, b2 reaches end
    b2.x = 1900.0
    b2.y = 1900.0

    mode.tick(world, [b1, b2], 1.0)

    assert 2 in mode.finished_players
    assert 1 not in mode.finished_players

    # Assert score recorded (lower time technically better, time = 2.0)
    lb = gm.get_mini_game_leaderboard("ObstacleGuild", "obstacle_course")
    # Time recorded, not 0
    assert len(lb) == 1
    assert lb[0]["score"] == 2.0
