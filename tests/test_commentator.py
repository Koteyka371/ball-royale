import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from ai.commentator import BattleCommentator

def test_commentator_empty_log():
    commentator = BattleCommentator()
    lines = commentator.generate_commentary([], {})
    assert lines == []

def test_commentator_first_blood_and_streaks():
    kill_log = [
        {"tick": 10, "killer_id": 1, "killer_type": "scout", "victim_id": 2, "victim_type": "tank"},
        {"tick": 20, "killer_id": 1, "killer_type": "scout", "victim_id": 3, "victim_type": "warrior"},
        {"tick": 30, "killer_id": 1, "killer_type": "scout", "victim_id": 4, "victim_type": "sniper"},
        {"tick": 40, "killer_id": 1, "killer_type": "scout", "victim_id": 5, "victim_type": "healer"}
    ]
    stats = {"winner": "scout", "longest_killstreak": 4}

    commentator = BattleCommentator()
    lines = commentator.generate_commentary(kill_log, stats)

    assert any("[FIRST BLOOD] The scout #1 drew first blood by eliminating tank #2!" in line for line in lines)
    assert any("[DOUBLE KILL] scout #1 is heating up!" in line for line in lines)
    assert any("[TRIPLE KILL] scout #1 is unstoppable!" in line for line in lines)
    assert any("[RAMPAGE] scout #1 is on a rampage!" in line for line in lines)
    assert any("[VICTORY] The scout type emerged victorious!" in line for line in lines)

def test_commentator_victim_streak_reset():
    kill_log = [
        {"tick": 10, "killer_id": 2, "killer_type": "tank", "victim_id": 3, "victim_type": "warrior"},
        {"tick": 20, "killer_id": 2, "killer_type": "tank", "victim_id": 4, "victim_type": "warrior"},
        {"tick": 30, "killer_id": 1, "killer_type": "scout", "victim_id": 2, "victim_type": "tank"},
        {"tick": 40, "killer_id": 1, "killer_type": "scout", "victim_id": 5, "victim_type": "warrior"}
    ]
    stats = {"winner": "scout", "longest_killstreak": 2}

    commentator = BattleCommentator()
    lines = commentator.generate_commentary(kill_log, stats)

    assert any("[DOUBLE KILL] tank #2 is heating up!" in line for line in lines)
    assert any("[Tick 30] The scout #1 brutally eliminated tank #2!" in line for line in lines)
    assert any("[DOUBLE KILL] scout #1 is heating up!" in line for line in lines)

def test_commentator_draw():
    kill_log = [
        {"tick": 10, "killer_id": 1, "killer_type": "scout", "victim_id": 2, "victim_type": "tank"}
    ]
    stats = {"winner": None, "longest_killstreak": 1}

    commentator = BattleCommentator()
    lines = commentator.generate_commentary(kill_log, stats)

    assert any("[DRAW] Nobody survived the carnage!" in line for line in lines)

def test_commentator_weather_change():
    kill_log = [
        {"tick": 10, "type": "weather_change", "weather": "rain"}
    ]
    stats = {"winner": None, "longest_killstreak": 0}
    commentator = BattleCommentator()
    lines = commentator.generate_commentary(kill_log, stats)
    assert any("[WEATHER] The weather has shifted to RAIN! Adapt or perish!" in line for line in lines)
