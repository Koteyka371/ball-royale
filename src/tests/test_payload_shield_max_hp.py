from ai.game_modes import DualPayloadMode, EscortMode
from unittest.mock import MagicMock
import pytest

class MockBall:
    def __init__(self, ball_type="normal", team="Red", x=0, y=0, hp=100.0, max_hp=100.0):
        self.ball_type = ball_type
        self.team = team
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = max_hp
        self.alive = True
        self.shield = 0.0

def test_dual_payload_heal_max_hp():
    mode = DualPayloadMode()
    world = MagicMock()
    # Dummy modifiers to avoid KeyError
    world.modifiers = ["dummy"]
    world.weekly_mutator = ""
    world.mutators = []

    red_payload = MockBall(ball_type="payload", team="Red", x=100, y=500)
    red_payload.is_payload = True

    red_player = MockBall(team="Red", x=100, y=500, hp=100.0, max_hp=100.0)

    balls = [red_payload, red_player]
    # We bypass setup() if we mock payload directly, or we can just mock leaderboards etc
    # mode.setup(world, balls) - bypass because of too many mock dependencies
    mode.payload_red = red_payload

    # Tick with delta 1.0 to get 15 healing
    mode.tick(world, balls, delta=1.0)

    # Should still be at max_hp, but should have gained 15 shield!
    assert red_player.hp == 100.0
    assert getattr(red_player, 'shield', 0.0) == 15.0

def test_escort_heal_max_hp():
    mode = EscortMode()
    world = MagicMock()

    payload = MockBall(ball_type="payload", team="Defenders", x=100, y=500)
    payload.is_payload = True

    player = MockBall(team="Defenders", x=100, y=500, hp=100.0, max_hp=100.0)

    balls = [payload, player]
    mode.payload = payload

    mode.tick(world, balls, delta=1.0)

    assert player.hp == 100.0
    assert getattr(player, 'shield', 0.0) == 15.0
