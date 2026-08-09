import pytest
from typing import List, Dict, Any
from unittest.mock import MagicMock
from system.crowd_system import CrowdSystem

class DummyBall:
    def __init__(self, id, team, alive=True, killer=None):
        self.id = id
        self.team = team
        self.alive = alive
        self.killer = killer

class DummyPM:
    def __init__(self):
        self.data = {"skill_points": 1000, "prestige_tokens": 50, "loyalty_points": 100}
    def save(self):
        pass

def test_juggernaut_survival_bet():
    world = MagicMock()
    world.profile_manager = DummyPM()
    world.events = []

    def add_event(evt_type, data):
        world.events.append((evt_type, data))
    world.add_event = add_event

    sys = CrowdSystem(world)

    # 1) Start game with Juggernaut
    balls = [
        DummyBall(1, "Juggernaut"),
        DummyBall(2, "Player")
    ]
    kill_log = []
    sys.tick(balls, kill_log, 100)  # initializes jugg
    assert sys.current_juggernaut_id == 1
    assert sys.juggernaut_start_tick == 100

    # 2) Place bet on survival time (e.g., 20 seconds = 1200 ticks)
    # The command is !bet jugg_time 20 100sp
    sys.queue_external_command("user1", "!bet jugg_time 20 100sp")
    sys.tick(balls, kill_log, 105)
    assert len(sys.juggernaut_bets) == 1
    assert world.profile_manager.data["skill_points"] == 900

    # 3) Fast forward time and kill Juggernaut
    # target_time is 20s. Let's make him survive exactly 20 seconds.
    # 20s * 60 ticks/s = 1200 ticks. So death at tick 1300.
    balls[0].alive = False
    balls[0].killer = 2
    sys.tick(balls, kill_log, 1300)

    # Payout should be made: bet amount 100 * multiplier 3.0 = 300
    # Original balance 1000 - 100 (bet) + 300 (win) = 1200
    assert world.profile_manager.data["skill_points"] == 1200
    assert len(sys.juggernaut_bets) == 0

def test_juggernaut_killer_bet():
    world = MagicMock()
    world.profile_manager = DummyPM()
    world.events = []

    def add_event(evt_type, data):
        world.events.append((evt_type, data))
    world.add_event = add_event

    sys = CrowdSystem(world)

    balls = [
        DummyBall(1, "Juggernaut"),
        DummyBall(5, "Player")
    ]
    kill_log = []
    sys.tick(balls, kill_log, 50)
    assert sys.current_juggernaut_id == 1

    # !bet jugg_killer 5 10pt
    sys.queue_external_command("user2", "!bet jugg_killer 5 10pt")
    sys.tick(balls, kill_log, 55)

    assert world.profile_manager.data["prestige_tokens"] == 40
    assert sys.juggernaut_bets[0]["type"] == "killer"
    assert sys.juggernaut_bets[0]["target_killer"] == 5

    # Kill juggernaut
    kill_log = [{"victim_id": 1, "killer_id": 5}]
    balls[0].alive = False

    sys.tick(balls, kill_log, 600)

    # Win condition: amount 10 * multiplier 5.0 = 50. Total 40 + 50 = 90
    assert world.profile_manager.data["prestige_tokens"] == 90
