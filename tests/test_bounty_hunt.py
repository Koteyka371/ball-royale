import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.game_modes import BountyHuntMode
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, id, team, hp=100):
        self.id = id
        self.team = team
        self.hp = hp
        self.attack = 10
        self.defense = 10
        self.speed = 10
        self.skill_points = 0

class MockWorld:
    pass

def test_bounty_hunt_mode():
    mode = GAME_MODES.get("bounty_hunt", None)
    if not mode:
        mode = BountyHuntMode()

    world = MockWorld()
    balls = [
        MockBall(1, "red"),
        MockBall(2, "red"),
        MockBall(3, "blue"),
        MockBall(4, "blue"),
    ]

    # Tick 1: Bounties selected
    mode.tick(world, balls, 0.1)
    assert mode.bounty_selected
    assert "red" in mode.bounties
    assert "blue" in mode.bounties

    # Tick 2: Bounties alive, no buffs
    mode.tick(world, balls, 0.1)
    assert mode.buff_active_for_team is None

    # Destroy red's bounty
    red_bounty_id = mode.bounties["red"]
    for b in balls:
        if b.id == red_bounty_id:
            b.hp = 0

    # Tick 3: Blue team should get buff
    mode.tick(world, balls, 0.1)
    assert mode.buff_active_for_team == "blue"

    # Check if blue got buffed
    for b in balls:
        if b.team == "blue":
            assert b.attack > 10
            assert b.defense > 10
            assert b.speed > 10
            assert b.skill_points > 0
