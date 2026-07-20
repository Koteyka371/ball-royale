import pytest
from system.crowd_system import CrowdSystem

class MockWorld:
    def __init__(self):
        self.events = []

    def add_event(self, event_type, data=None):
        self.events.append((event_type, data or {}))


class MockBall:
    def __init__(self, **kwargs):
        self.id = 1
        self.alive = True
        self.ball_type = "player"
        self.x = 0.0
        self.y = 0.0
        self.score = 0
        self.max_stamina = 100
        self.stamina = 100
        self.base_speed = 100
        self.speed = 100
        self.base_damage = 10
        self.original_base_damage = 10
        self.traits = []
        self.weather_immunity_timer = 0
        self.in_mirror_dimension = False
        self.intangible = False
        self.vision_radius = 200
        self.invisible = False

        for k, v in kwargs.items():
            setattr(self, k, v)


def test_bounty_placed():
    world = MockWorld()
    system = CrowdSystem(world)
    b1 = MockBall(id=1)

    system.process_external_command("User1", "!bounty 1", [b1])

    assert system.active_bounty is not None
    assert system.active_bounty["target_id"] == 1
    assert system.active_bounty["user"] == "User1"

    found_placed = False
    for t, d in world.events:
        if t == "visual_effect" and d.get("type") == "bounty_placed":
            found_placed = True
    assert found_placed


def test_bounty_claimed():
    world = MockWorld()
    system = CrowdSystem(world)
    target = MockBall(id=1)
    killer = MockBall(id=2)

    # Place bounty
    system.process_external_command("User1", "!bounty 1", [target, killer])

    # Handle kill
    kill_info = {"killer_id": 2, "victim_id": 1}
    system._handle_kill(kill_info, 10, [target, killer])

    assert killer.score == 5000
    assert system.active_bounty is None

    found_claimed = False
    for t, d in world.events:
        if t == "visual_effect" and d.get("type") == "bounty_claimed":
            found_claimed = True
    assert found_claimed


def test_bounty_expired():
    world = MockWorld()
    system = CrowdSystem(world)
    target = MockBall(id=1)

    system.process_external_command("User1", "!bounty 1", [target])
    assert system.active_bounty is not None

    system.active_bounty["timer"] = 1
    system._process_bounties([target], 10)

    assert system.active_bounty is None
