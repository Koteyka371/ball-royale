import pytest
from src.system.crowd_system import CrowdSystem

class MockWorld:
    def __init__(self):
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, id, team, ball_type, alive=True):
        self.id = id
        self.team = team
        self.ball_type = ball_type
        self.alive = alive

def test_epic_kill_chants():
    world = MockWorld()
    system = CrowdSystem(world)

    balls = [
        MockBall(1, "team_a", "assassin"),
        MockBall(2, "team_b", "healer"),
        MockBall(3, "team_c", "berserker"),
        MockBall(4, "team_d", "sniper"),
        MockBall(5, "team_e", "generic"),
    ]

    # Tick 1: Assassin kill 1
    system.tick(balls, [{"tick": 1, "killer_id": 1, "victim_id": 2}], 1)
    # Exclude comeback cheer from this check
    assert not any(e[0] == "crowd_cheer" and "Assassin" in e[1].get("message", "") for e in world.events)

    # Tick 2: Assassin kill 2
    system.tick(balls, [{"tick": 1, "killer_id": 1, "victim_id": 2}, {"tick": 2, "killer_id": 1, "victim_id": 2}], 2)
    assert not any(e[0] == "crowd_cheer" and "Assassin" in e[1].get("message", "") for e in world.events)

    # Tick 3: Assassin kill 3 (Streak!)
    system.tick(balls, [
        {"tick": 1, "killer_id": 1, "victim_id": 2},
        {"tick": 2, "killer_id": 1, "victim_id": 2},
        {"tick": 3, "killer_id": 1, "victim_id": 2}
    ], 3)

    cheer_events = [e for e in world.events if e[0] == "crowd_cheer" and "Assassin" in e[1].get("message", "")]
    assert len(cheer_events) == 1

    world.events.clear()

    # Test Berserker
    system.kill_streak[3] = 2 # Simulate 2 kills
    system.tick(balls, [{"tick": 4, "killer_id": 3, "victim_id": 2}], 4)
    cheer_events = [e for e in world.events if e[0] == "crowd_cheer" and "Berserker" in e[1].get("message", "")]
    assert len(cheer_events) == 1

    world.events.clear()

    # Test Sniper
    system.kill_streak[4] = 2 # Simulate 2 kills
    system.tick(balls, [{"tick": 5, "killer_id": 4, "victim_id": 2}], 5)
    cheer_events = [e for e in world.events if e[0] == "crowd_cheer" and "One shot" in e[1].get("message", "")]
    assert len(cheer_events) == 1

    world.events.clear()

    # Test Generic
    system.kill_streak[5] = 2 # Simulate 2 kills
    system.tick(balls, [{"tick": 6, "killer_id": 5, "victim_id": 2}], 6)
    cheer_events = [e for e in world.events if e[0] == "crowd_cheer" and "Generic" in e[1].get("message", "")]
    assert len(cheer_events) == 1

if __name__ == "__main__":
    test_epic_kill_chants()
    print("Tests passed!")
