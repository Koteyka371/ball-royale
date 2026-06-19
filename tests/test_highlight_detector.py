import pytest
from video.highlight_detector import HighlightDetector

def test_clutch_play_detection():
    detector = HighlightDetector()
    history = [
        {
            "tick": 10,
            "balls": [
                {"id": 1, "hp": 100, "max_hp": 100, "type": "basic"},
                {"id": 2, "hp": 4, "max_hp": 100, "type": "basic"}
            ]
        },
        {
            "tick": 11,
            "balls": [
                {"id": 1, "hp": 100, "max_hp": 100, "type": "basic"},
                {"id": 2, "hp": 4, "max_hp": 100, "type": "basic"}
            ]
        }
    ]

    highlights = detector.detect_highlights(history, [])

    clutch_highlights = [h for h in highlights if h["type"] == "clutch_play"]
    assert len(clutch_highlights) == 1
    assert clutch_highlights[0]["ball_id"] == 2
    assert clutch_highlights[0]["tick"] == 10

def test_epic_kill_detection():
    detector = HighlightDetector()
    kill_log = [
        {"tick": 10, "killer_id": 1, "victim_id": 2},
        {"tick": 20, "killer_id": 1, "victim_id": 3}, # streak = 2
        {"tick": 30, "killer_id": 1, "victim_id": 4}, # streak = 3
        {"tick": 80, "killer_id": 1, "victim_id": 5}, # streak = 1 (reset > 30 ticks)
    ]

    highlights = detector.detect_highlights([], kill_log)

    epic_highlights = [h for h in highlights if h["type"] == "epic_kill"]
    assert len(epic_highlights) == 2
    assert epic_highlights[0]["tick"] == 20
    assert "Double Kill" in epic_highlights[0]["description"]
    assert epic_highlights[1]["tick"] == 30
    assert "Triple Kill" in epic_highlights[1]["description"]

def test_1v1_finals_detection():
    detector = HighlightDetector()
    history = [
        {
            "tick": 100,
            "balls": [
                {"id": 1, "hp": 100, "type": "basic"},
                {"id": 2, "hp": 100, "type": "basic"},
                {"id": 3, "hp": 100, "type": "basic"}
            ]
        },
        {
            "tick": 101,
            "balls": [
                {"id": 1, "hp": 100, "type": "basic"},
                {"id": 2, "hp": 100, "type": "basic"},
                {"id": 3, "hp": 0, "type": "basic"} # Dies here
            ]
        },
        {
            "tick": 102,
            "balls": [
                {"id": 1, "hp": 100, "type": "basic"},
                {"id": 2, "hp": 50, "type": "basic"},
                {"id": 3, "hp": 0, "type": "basic"}
            ]
        }
    ]

    highlights = detector.detect_highlights(history, [])

    finals_highlights = [h for h in highlights if h["type"] == "1v1_finals"]
    assert len(finals_highlights) == 1
    assert finals_highlights[0]["tick"] == 101
    assert "1v1 Finals" in finals_highlights[0]["description"]
