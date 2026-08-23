import pytest
from ai.commentator import BattleCommentator

def test_commentary_strategy_analysis():
    commentator = BattleCommentator()
    kill_log = [
        {"type": "kill", "tick": 10, "killer_id": 1, "killer_type": "Tank", "victim_id": 2, "victim_type": "Sniper", "strategy": "flanking"},
    ]
    stats = {"winner": "Tank"}
    lines = commentator.generate_commentary(kill_log, stats)
    assert any("strategy" in line.lower() or "flanking" in line.lower() for line in lines)

def test_commentary_ai_voice(capsys):
    commentator = BattleCommentator()
    kill_log = [
        {"type": "kill", "tick": 10, "killer_id": 1, "killer_type": "Tank", "victim_id": 2, "victim_type": "Sniper"},
    ]
    stats = {"winner": "Tank"}

    # generate_commentary now internally calls synthesize_voice
    lines = commentator.generate_commentary(kill_log, stats)

    captured = capsys.readouterr()
    for line in lines:
        assert f"[VOICE SYNTHESIS]: {line}" in captured.out
