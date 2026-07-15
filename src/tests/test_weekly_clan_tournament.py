import os
import json
import pytest
from system.clan import ClanManager

def test_tournament(tmp_path):
    file_path = tmp_path / "test_clans.json"
    cm = ClanManager(str(file_path))
    cm.create_clan("ClanA", "p1")
    cm.create_clan("ClanB", "p2")
    cm.create_clan("ClanC", "p3")
    cm.create_clan("ClanD", "p4")

    assert cm.start_weekly_tournament() == True

    cm.add_tournament_points("ClanA", 500)
    cm.add_tournament_points("ClanB", 300)
    cm.add_tournament_points("ClanC", 100)
    cm.add_tournament_points("ClanD", 50)

    assert cm.end_weekly_tournament() == True

    assert cm.data["clans"]["ClanA"]["points"] == 5000
    assert "Weekly_Champion_Aura" in cm.data["clans"]["ClanA"]["cosmetics"]
    assert "Currency_Boost_Tier3" in cm.data["clans"]["ClanA"]["buffs"]

    assert cm.data["clans"]["ClanB"]["points"] == 3000
    assert "Currency_Boost_Tier2" in cm.data["clans"]["ClanB"]["buffs"]

    assert cm.data["clans"]["ClanC"]["points"] == 2000
    assert "Currency_Boost_Tier1" in cm.data["clans"]["ClanC"]["buffs"]
