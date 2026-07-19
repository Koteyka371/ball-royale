import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest # type: ignore
from ai.game_modes import GAME_MODES

class MockProfileManager:
    def __init__(self):
        self.points = 0
    def add_skill_points(self, pts):
        self.points += pts

class MockWorld:
    def __init__(self):
        self.events = []
        self.profile_manager = MockProfileManager()
        self.dead_balls = []

    def add_event(self, type_, data):
        self.events.append((type_, data))

class MockBall:
    def __init__(self, id, ball_type="warrior", team="Red"):
        self.id = id
        self.ball_type = ball_type
        self.alive = True
        self.team = team
        self.base_damage = 10.0
        self.max_hp = 100.0
        self.hp = 100.0
        self.vision_radius = 500.0
        self.is_bounty = False
        self.x = 0.0
        self.y = 0.0

def test_bounty_tag_mode():
    mode = GAME_MODES["bounty_tag"]
    world = MockWorld()

    balls = [MockBall(1), MockBall(2, team="Blue")]
    mode.setup(world, balls)

    bounty_id = mode.current_bounty_id
    assert bounty_id in [1, 2]

    bounty_ball = next(b for b in balls if b.id == bounty_id)
    assert bounty_ball.is_bounty == True
    assert bounty_ball.max_hp == 200.0
    assert bounty_ball.base_damage == 15.0
    assert bounty_ball.vision_radius == 750.0

    # Simulate ticks
    mode.tick(world, balls, 1.0)
    mode.tick(world, balls, 1.0)
    assert mode.bounty_time_held[bounty_id] == 2.0

    # Check ping
    pings = [e for e in world.events if e[0] == "bounty_compass"]
    assert len(pings) > 0

    # Move the bounty ball to increase distance
    bounty_ball.x += 100
    bounty_ball.y += 0
    mode.tick(world, balls, 1.0)

    # distance = 100. bonus = 5. base = 30 * 2 * 2.0 = 120
    # expected = 125

    # Kill bounty
    bounty_ball.kill_bounty = 2
    bounty_ball.alive = False
    killer = balls[0] if bounty_ball.id == 2 else balls[1]
    mode.on_ball_died(world, bounty_ball, killer)

    assert mode.current_bounty_id == killer.id
    assert killer.max_hp == 200.0

    assert world.profile_manager.points == 125

    # Test winner
    bounty_ball.alive = False
    killer.alive = False
    winner = mode.check_winner(world, balls)
    assert winner == str(bounty_id) or winner == bounty_ball.team
