import pytest
from ui.stats_overlay import StatsOverlay

def test_stats_overlay_initialization():
    overlay = StatsOverlay()
    assert overlay.stats["alive"] == 0
    assert overlay.stats["total_kills"] == 0
    assert overlay.stats["top_killstreak"] == 0
    assert overlay.stats["fps"] == 60
    assert overlay.stats["tick"] == 0
    assert overlay.visible is True

def test_stats_overlay_update():
    overlay = StatsOverlay()
    battle_stats = {
        "survivors": 10,
        "total_kills": 5,
        "longest_killstreak": 3
    }
    overlay.update(battle_stats, current_tick=100, fps=55)

    assert overlay.stats["tick"] == 100
    assert overlay.stats["fps"] == 55
    assert overlay.stats["alive"] == 10
    assert overlay.stats["total_kills"] == 5
    assert overlay.stats["top_killstreak"] == 3

def test_stats_overlay_update_fallback_alive():
    overlay = StatsOverlay()
    battle_stats = {
        "ball_types_alive": {"warrior": 2, "tank": 3},
        "total_kills": 1,
        "longest_killstreak": 1
    }
    overlay.update(battle_stats, current_tick=50, fps=60)

    assert overlay.stats["alive"] == 5

def test_stats_overlay_display():
    overlay = StatsOverlay()
    battle_stats = {
        "survivors": 42,
        "total_kills": 99,
        "longest_killstreak": 10
    }
    overlay.update(battle_stats, current_tick=500, fps=120)

    display = overlay.get_text_display()
    assert "Tick: 500" in display
    assert "FPS: 120" in display
    assert "Alive: 42" in display
    assert "Total Kills: 99" in display
    assert "Top Killstreak: 10" in display

def test_stats_overlay_toggle_visibility():
    overlay = StatsOverlay()
    assert overlay.visible is True
    assert "=== STATS ===" in overlay.get_text_display()

    overlay.toggle_visibility()
    assert overlay.visible is False
    assert overlay.get_text_display() == ""

    overlay.toggle_visibility()
    assert overlay.visible is True
    assert "=== STATS ===" in overlay.get_text_display()
