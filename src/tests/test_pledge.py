import pytest
from unittest.mock import MagicMock
from system.crowd_system import CrowdSystem

def test_pledge_and_spawn():
    world = MagicMock()
    world.events = []

    def add_event(name, data):
        world.events.append((name, data))

    world.add_event = add_event

    system = CrowdSystem(world)

    b1 = MagicMock(alive=True, ball_type="Player", team="red", id=1)
    b2 = MagicMock(alive=True, ball_type="Player", team="blue", id=2)
    b3 = MagicMock(alive=True, ball_type="Player", team="green", id=3)

    system.process_external_command("user1", "!pledge red", [b1, b2, b3])

    # Check cheer event
    assert len(world.events) == 1
    assert world.events[0][0] == "crowd_cheer"

    world.events.clear()

    # Spawn hazard - should target enemies (blue or green) and have owner_team="red"
    system.process_external_command("user1", "!spawn spike_trap", [b1, b2, b3])

    hazard_events = [e for e in world.events if e[0] == "spawn_hazard"]
    assert len(hazard_events) == 1
    assert hazard_events[0][1]["owner_team"] == "red"

    # Check drop - should target friends (red) and have team="red"
    world.events.clear()
    system.process_external_command("user1", "!drop health", [b1, b2, b3])

    booster_events = [e for e in world.events if e[0] == "spawn_booster"]
    assert len(booster_events) == 1
    assert booster_events[0][1]["team"] == "red"
