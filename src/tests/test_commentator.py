from ai.commentator import BattleCommentator

def test_commentary_clutch_play():
    commentator = BattleCommentator()
    kill_log = [
        {"type": "kill", "tick": 10, "killer_id": 1, "killer_type": "Tank", "victim_id": 2, "victim_type": "Sniper", "killer_build": "Juggernaut", "clutch": True},
    ]
    stats = {"winner": "Tank"}
    lines = commentator.generate_commentary(kill_log, stats)
    assert any("clutch" in line.lower() for line in lines)

def test_commentary_build_personalization():
    commentator = BattleCommentator()
    kill_log = [
        {"type": "kill", "tick": 10, "killer_id": 1, "killer_type": "Tank", "victim_id": 2, "victim_type": "Sniper", "killer_build": "Juggernaut"},
    ]
    stats = {"winner": "Tank"}
    lines = commentator.generate_commentary(kill_log, stats)
    assert any("juggernaut" in line.lower() for line in lines)
