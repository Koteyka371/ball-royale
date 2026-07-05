import sys
import os
import pytest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/')))
from ai.game_modes import GuildVsGuildTournamentMode


class MockBall:
    def __init__(self, id, x, y, alive=True):
        self.id = id
        self.x = x
        self.y = y
        self.alive = alive
        self.max_hp = 100.0
        self.hp = 100.0
        self.team = None
        self.ball_type = "normal"

class MockWorld:
    def __init__(self):
        self.balls = []
        self.dead_balls = []
        self.profile_manager = MagicMock()
        del self.profile_manager.leaderboard_manager

def test_gvg_tournament_setup():
    mode = GuildVsGuildTournamentMode()
    world = MockWorld()

    balls = [MockBall(i, i*10, i*10) for i in range(4)]
    mode.setup(world, balls)

    assert balls[0].team == "Red"
    assert balls[1].team == "Red"
    assert balls[2].team == "Blue"
    assert balls[3].team == "Blue"
    assert len(mode.initial_positions) == 4

def test_gvg_tournament_tick_and_winner():
    mode = GuildVsGuildTournamentMode()
    world = MockWorld()

    b1 = MockBall(1, 10, 10)
    b2 = MockBall(2, 20, 20)
    balls = [b1, b2]
    mode.setup(world, balls)

    assert mode.current_round == 1
    assert mode.team_wins["Red"] == 0
    assert mode.team_wins["Blue"] == 0

    # Simulate Red team dying
    b1.alive = False
    mode.tick(world, balls, 0.1)

    # Round should be over
    assert mode.round_active == False
    assert mode.team_wins["Blue"] == 1

    # Wait for round delay
    mode.tick(world, balls, 3.1)

    # Next round should start
    assert mode.round_active == True
    assert mode.current_round == 2
    assert b1.alive == True # Revived

    # Simulate Red team dying again
    b1.alive = False
    mode.tick(world, balls, 0.1)

    assert mode.round_active == False
    assert mode.team_wins["Blue"] == 2

    winner = mode.check_winner(world, balls)
    assert winner == "Blue"
    world.profile_manager.add_cosmetic.assert_called_with("Tournament Champion")
    world.profile_manager.add_title.assert_called_with("Clan Legend")
