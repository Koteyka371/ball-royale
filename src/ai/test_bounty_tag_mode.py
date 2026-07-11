import pytest # type: ignore
from ai.game_modes import BountyTagMode

class MockWorld:
    def __init__(self):
        self.events = []

    def add_event(self, type_, data):
        self.events.append((type_, data))

class MockBall:
    def __init__(self, id, ball_type="warrior"):
        self.id = id
        self.ball_type = ball_type
        self.alive = True
        self.team = "Red"
        self.base_damage = 10.0
        self.base_speed = 100.0
        self.max_hp = 100.0
        self.hp = 100.0
        self.x = 0.0
        self.y = 0.0

def test_bounty_tag_mode():
    mode = BountyTagMode()
    world = MockWorld()

    balls = [MockBall(1), MockBall(2), MockBall(3)]
    mode.setup(world, balls)

    assert mode.bounty_id is not None
    initial_bounty_id = mode.bounty_id
    assert any("first Bounty" in e[1].get("message", "") for e in world.events)

    mode.tick(world, balls, 1.0)

    # Bounty ball should have buffs
    bounty_ball = next(b for b in balls if b.id == initial_bounty_id)
    assert getattr(bounty_ball, "damage_multiplier", 1.0) == 1.5
    assert getattr(bounty_ball, "speed_multiplier", 1.0) == 1.5
    assert getattr(bounty_ball, "perception_radius", 0.0) == 500.0

    # Fast forward to trigger ping
    mode.tick(world, balls, 2.0)
    assert any(e[0] == "minimap_ping" for e in world.events)

    # Steal the bounty
    bounty_ball.alive = False
    other_ball = next(b for b in balls if b.id != initial_bounty_id)
    bounty_ball.last_damaged_by = other_ball.id

    mode.tick(world, balls, 0.1)

    assert mode.bounty_id == other_ball.id
    assert any("stole the Bounty" in e[1].get("message", "") for e in world.events)

    # Check winner when only 1 alive
    balls[2].alive = False
    winner = mode.check_winner(world, balls)

    # other_ball is alive, other_ball's team should win
    # wait, they are all on Red team! So winner should be Red, or the ID.
    # We assigned team "Red", so the winner should be "Red".
    # Winner logic depends on alive_count == 1.
    # In the test, we only killed balls[2], so 2 are still alive (1 is dead). Wait, balls[0] is dead too!
    # Initial bounty was balls[0] or balls[1]. Let's just kill everything except other_ball.
    for b in balls:
        if b.id != other_ball.id:
            b.alive = False
    winner = mode.check_winner(world, balls)
    assert winner == "Red"
