import sys
import os
import math

from ui.bounty_indicator.bounty_indicator import BountyIndicatorUI

def test_bounty_indicator_creation():
    ui = BountyIndicatorUI(1920, 1080)
    assert ui.screen_width == 1920
    assert ui.screen_height == 1080
    assert len(ui.active_indicators) == 0

def test_bounty_indicator_update():
    ui = BountyIndicatorUI(800, 600)
    events = [
        {"type": "kill", "data": {}},
        {"type": "bounty_compass", "data": {"target_x": 1000.0, "target_y": 500.0, "owner_id": 1}},
        {"type": "bounty_compass", "data": {"target_x": -500.0, "target_y": -500.0, "owner_id": 2}}
    ]

    # Test as spectator (all indicators)
    ui.update(events)
    assert len(ui.active_indicators) == 2
    assert ui.active_indicators[0]["target_x"] == 1000.0

    # Test as specific player
    ui.update(events, local_player_id=1)
    assert len(ui.active_indicators) == 1
    assert ui.active_indicators[0]["target_x"] == 1000.0

    # Test as player with no compass events
    ui.update(events, local_player_id=3)
    assert len(ui.active_indicators) == 0

def test_bounty_indicator_render_data():
    ui = BountyIndicatorUI(800, 600)

    events = [
        {"type": "bounty_compass", "data": {"target_x": 1000.0, "target_y": 300.0, "owner_id": 1}}
    ]
    ui.update(events)

    # Camera at (0, 300), target at (1000, 300) -> Target is to the right
    # Screen is 800x600, half_width is 400. Distance is 1000, so it's outside.
    render_data = ui.get_render_data(0.0, 300.0, 1.0)

    assert len(render_data) == 1
    pointer = render_data[0]
    assert pointer["type"] == "bounty_pointer"
    assert pointer["color"] == "orange"

    # Angle should point directly right (0 radians)
    assert math.isclose(pointer["angle"], 0.0, abs_tol=0.01)

    # X should be at the right edge minus margin
    # center_x (400) + screen_dx (370) = 770
    assert math.isclose(pointer["x"], 770.0, abs_tol=0.01)

    # Y should be exactly centered
    assert math.isclose(pointer["y"], 300.0, abs_tol=0.01)

def test_bounty_indicator_inside_view():
    ui = BountyIndicatorUI(800, 600)

    events = [
        {"type": "bounty_compass", "data": {"target_x": 100.0, "target_y": 100.0, "owner_id": 1}}
    ]
    ui.update(events)

    # Camera at (0, 0), target at (100, 100) -> Target is within view (half w/h are 400/300)
    render_data = ui.get_render_data(0.0, 0.0, 1.0)

    # Should not render a pointer if the target is on screen
    assert len(render_data) == 0

def test_nemesis_indicator_render_data():
    ui = BountyIndicatorUI(800, 600)

    events = [
        {"type": "nemesis_compass", "data": {"target_x": -1000.0, "target_y": -300.0, "owner_id": 1}}
    ]
    ui.update(events, local_player_id=1)

    # Camera at (0, -300), target at (-1000, -300) -> Target is to the left
    render_data = ui.get_render_data(0.0, -300.0, 1.0)

    assert len(render_data) == 1
    pointer = render_data[0]
    assert pointer["type"] == "nemesis_pointer"
    assert pointer["color"] == "purple"

    # Angle should point directly left (pi or -pi)
    assert math.isclose(abs(pointer["angle"]), math.pi, abs_tol=0.01)

    # X should be at the left edge plus margin
    # center_x (400) - screen_dx (370) = 30
    assert math.isclose(pointer["x"], 30.0, abs_tol=0.01)

    # Y should be exactly centered
    assert math.isclose(pointer["y"], 300.0, abs_tol=0.01)
