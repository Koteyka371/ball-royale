import pytest
from ai.action import Action
from ai.game_modes import GameMode, BattleRoyaleMode

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.items = []
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.game_mode = BattleRoyaleMode()
        self.game_mode.zone_target_x = 750.0
        self.game_mode.zone_target_y = 250.0
        self.delta = 0.016
        self.events = []
        self.boosters = []

    def add_event(self, event_type, data):
        self.events.append({"type": event_type, "data": data})

class MockBall:
    def __init__(self):
        self.id = 1
        self.x = 500.0
        self.y = 500.0
        self.inventory = []
        self.use_item = False
        self.safe_zone_radar_timer = 0.0

def test_safe_zone_radar_usage():
    world = MockWorld()
    ball = MockBall()

    ball.inventory.append("safe_zone_radar")
    ball.use_item = True

    action = Action(ball, world)
    action.execute("default", world.delta)

    assert "safe_zone_radar" not in ball.inventory
    assert getattr(ball, "safe_zone_radar_target_x", 0) == 750.0
    assert getattr(ball, "safe_zone_radar_target_y", 0) == 250.0
    assert ball.safe_zone_radar_timer > 0.0

    # Check visual event
    radar_events = [e for e in world.events if e["type"] == "visual_effect" and e["data"].get("type") == "radar_ping"]
    assert len(radar_events) == 1
    assert radar_events[0]["data"]["x"] == 750.0

def test_safe_zone_radar_timer_tick():
    world = MockWorld()
    ball = MockBall()
    ball.safe_zone_radar_timer = 0.03

    action = Action(ball, world)
    action.execute("default", 0.016)

    # 0.03 - 0.016 = 0.014
    assert ball.safe_zone_radar_timer < 0.015 and ball.safe_zone_radar_timer > 0.013

    action.execute("default", 0.016)

    assert ball.safe_zone_radar_timer == 0.0
