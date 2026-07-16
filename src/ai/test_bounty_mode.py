import pytest # type: ignore
from ai.game_modes import BountyHuntMode

class MockWorld:
    def __init__(self):
        self.dead_balls = []
        self.events = []

        class DummyLeaderboardManager:
            def __init__(self):
                self.data = {"current_season": 0}  # No modifiers for season 0
        self.leaderboard_manager = DummyLeaderboardManager()

    def add_event(self, type_, data):
        self.events.append((type_, data))

class MockBall:
    def __init__(self, id, ball_type="warrior"):
        self.id = id
        self.ball_type = ball_type
        self.alive = True
        self.team = None
        self.base_damage = 10.0
        self.base_speed = 100.0
        self.max_hp = 100.0
        self.hp = 100.0
        self.is_bounty = False
        self.bounty_timer = 0
        self.skill_uses = 0

def test_bounty_hunt_mode():
    mode = BountyHuntMode()
    world = MockWorld()

    # 4 balls, so 2 Red and 2 Blue
    balls = [MockBall(1), MockBall(2), MockBall(3), MockBall(4)]
    mode.setup(world, balls)

    # Check teams
    assert balls[0].team == "Red"
    assert balls[1].team == "Red"
    assert balls[2].team == "Blue"
    assert balls[3].team == "Blue"

    # Check bounties
    red_bounties = sum(1 for b in balls[:2] if getattr(b, "is_bounty", False))
    blue_bounties = sum(1 for b in balls[2:] if getattr(b, "is_bounty", False))

    assert red_bounties == 1
    assert blue_bounties == 1

    # Identify the Red bounty
    red_bounty = next(b for b in balls[:2] if getattr(b, "is_bounty", False))

    # Ensure Blue balls have base stats before Red bounty is destroyed
    assert balls[2].base_damage in [10.0, 20.0]
    assert balls[2].base_speed in [100.0, 150.0]
    assert balls[2].skill_uses == 0

    # Kill the Red bounty
    red_bounty.alive = False

    # Simulate a tick
    mode.tick(world, balls, 0.1)

    # Check that Blue team got buffed
    assert balls[2].base_damage in [20.0, 40.0] # 10 * 2.0
    assert balls[2].base_speed in [150.0, 225.0] # 100 * 1.5
    assert balls[2].max_hp == 150.0 # 100 * 1.5
    assert balls[2].hp == 150.0
    assert balls[2].skill_uses == 3

    # Check event was added
    assert any("Bounty destroyed" in e[1]["message"] for e in world.events)

    # Verify winner logic
    # Blue team is alive, Red team has one alive and one dead
    assert mode.check_winner(world, balls) is None

    balls[0].alive = False
    balls[1].alive = False
    assert mode.check_winner(world, balls) == "Blue"
