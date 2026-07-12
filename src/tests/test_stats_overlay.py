import sys
sys.path.insert(0, 'src')

from ui.stats_overlay import StatsOverlay

def test_stats_initialization():
    overlay = StatsOverlay(max_top_killers=2)
    assert overlay.max_top_killers == 2
    assert overlay.get_stats()["alive_count"] == 0

def test_stats_update():
    overlay = StatsOverlay(max_top_killers=2)
    balls = [
        {"id": 1, "type": "warrior", "hp": 100, "kills": 3},
        {"id": 2, "type": "tank", "hp": 0, "kills": 1},
        {"id": 3, "type": "scout", "hp": 50, "kills": 5},
        {"id": 4, "type": "sniper", "hp": 70, "kills": 0},
    ]
    overlay.update(balls)
    stats = overlay.get_stats()

    assert stats["alive_count"] == 3
    assert stats["total_kills"] == 9
    assert len(stats["top_killers"]) == 2
    assert stats["top_killers"][0]["id"] == 3
    assert stats["top_killers"][0]["kills"] == 5
    assert stats["top_killers"][1]["id"] == 1
    assert stats["top_killers"][1]["kills"] == 3

def test_stats_format_text():
    overlay = StatsOverlay(max_top_killers=2)
    balls = [
        {"id": 1, "type": "warrior", "hp": 100, "kills": 3},
        {"id": 3, "type": "scout", "hp": 50, "kills": 5},
    ]
    overlay.update(balls)
    text = overlay.format_text()
    assert "Alive: 2" in text
    assert "Total Kills: 8" in text
    assert "SCOUT-3: 5 kills" in text
    assert "WARRIOR-1: 3 kills" in text
