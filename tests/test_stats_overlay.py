import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from ui.stats_overlay import StatsOverlay

def test_stats_overlay_initialization():
    overlay = StatsOverlay()
    assert overlay.stats["ticks"] == 0
    assert overlay.stats["total_kills"] == 0
    assert overlay.stats["survivors"] == 0

def test_stats_overlay_update():
    overlay = StatsOverlay()
    stats = {
        "ticks": 100,
        "total_kills": 5,
        "survivors": 10,
        "winner": "warrior",
        "some_random_stat_we_dont_track": "ignored"
    }
    overlay.update(stats)
    assert overlay.stats["ticks"] == 100
    assert overlay.stats["total_kills"] == 5
    assert overlay.stats["survivors"] == 10
    assert overlay.stats["winner"] == "warrior"
    assert "some_random_stat_we_dont_track" not in overlay.stats

def test_stats_overlay_format():
    overlay = StatsOverlay()
    stats = {
        "ticks": 500,
        "battle_duration": 15.5,
        "total_kills": 40,
        "survivors": 10,
        "winner": "tank",
        "longest_killstreak": 5,
        "avg_hp_at_end": 45.2,
        "ball_types_alive": {"tank": 8, "healer": 2}
    }
    overlay.update(stats)
    lines = overlay.get_display_lines()

    assert lines[0] == "=== BATTLE STATS ==="
    assert lines[1] == "Time: 15.5s (Ticks: 500)"
    assert lines[2] == "Survivors: 10  |  Kills: 40"
    assert "Winner: TANK" in lines
    assert "Highest Killstreak: 5" in lines
    assert "Avg End HP: 45.2" in lines
    assert "Alive Types: tank: 8, healer: 2" in lines

def test_stats_overlay_format_no_winner():
    overlay = StatsOverlay()
    lines = overlay.get_display_lines()
    assert "Winner: None" in lines
