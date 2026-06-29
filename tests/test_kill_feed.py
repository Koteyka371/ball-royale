import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from ui.kill_feed import KillFeed

def test_kill_feed_empty():
    feed = KillFeed()
    assert len(feed.get_messages()) == 0

def test_kill_feed_update_formatting():
    feed = KillFeed()
    log = [
        {"tick": 10, "killer_id": 1, "killer_type": "warrior", "victim_id": 2, "victim_type": "tank"}
    ]
    feed.update(log)
    messages = feed.get_messages()
    assert len(messages) == 1
    assert messages[0] == "Tick 10: WARRIOR-1 killed TANK-2"

def test_kill_feed_max_lines():
    feed = KillFeed(max_lines=2)
    log = [
        {"tick": 1, "killer_id": 1, "killer_type": "a", "victim_id": 2, "victim_type": "b"},
        {"tick": 2, "killer_id": 3, "killer_type": "c", "victim_id": 4, "victim_type": "d"},
        {"tick": 3, "killer_id": 5, "killer_type": "e", "victim_id": 6, "victim_type": "f"}
    ]
    feed.update(log)
    messages = feed.get_messages()
    assert len(messages) == 2
    assert "Tick 2" in messages[0]
    assert "Tick 3" in messages[1]

def test_kill_feed_multiple_kills_same_tick():
    feed = KillFeed()
    log = [
        {"tick": 10, "killer_id": 1, "killer_type": "a", "victim_id": 2, "victim_type": "b"},
        {"tick": 10, "killer_id": 3, "killer_type": "c", "victim_id": 4, "victim_type": "d"}
    ]
    feed.update(log)
    messages = feed.get_messages()
    assert len(messages) == 2
    assert "Tick 10" in messages[0]
    assert "Tick 10" in messages[1]

def test_kill_feed_ignore_processed_ticks():
    feed = KillFeed()
    log1 = [{"tick": 10, "killer_id": 1, "killer_type": "a", "victim_id": 2, "victim_type": "b"}]
    feed.update(log1)

    log2 = [
        {"tick": 10, "killer_id": 1, "killer_type": "a", "victim_id": 2, "victim_type": "b"},
        {"tick": 15, "killer_id": 5, "killer_type": "e", "victim_id": 6, "victim_type": "f"}
    ]
    feed.update(log2)

    messages = feed.get_messages()
    assert len(messages) == 2
    assert "Tick 10" in messages[0]
    assert "Tick 15" in messages[1]

def test_kill_feed_clear():
    feed = KillFeed()
    log = [{"tick": 10, "killer_id": 1, "killer_type": "a", "victim_id": 2, "victim_type": "b"}]
    feed.update(log)
    assert len(feed.get_messages()) == 1
    feed.clear()
    assert len(feed.get_messages()) == 0

    log2 = [{"tick": 5, "killer_id": 3, "killer_type": "c", "victim_id": 4, "victim_type": "d"}]
    feed.update(log2)
    assert len(feed.get_messages()) == 1
    assert "Tick 5" in feed.get_messages()[0]

def test_kill_feed_weather_change():
    feed = KillFeed()
    log = [{"tick": 20, "type": "weather_change", "weather": "snow"}]
    feed.update(log)
    messages = feed.get_messages()
    assert len(messages) == 1
    assert "Weather changed to SNOW!" in messages[0]

def test_kill_feed_weather_warning():
    feed = KillFeed()
    log = [{"tick": 15, "type": "weather_warning", "weather": "rain"}]
    feed.update(log)
    messages = feed.get_messages()
    assert len(messages) == 1
    assert "WARNING! RAIN approaching!" in messages[0]
