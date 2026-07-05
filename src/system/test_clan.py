import os
import json
import pytest
from system.clan import ClanManager

@pytest.fixture
def temp_clan_file(tmp_path):
    file_path = tmp_path / "test_clans.json"
    yield str(file_path)

def test_create_clan(temp_clan_file):
    cm = ClanManager(temp_clan_file)
    assert cm.create_clan("TestClan", "player1") == True
    assert cm.create_clan("TestClan", "player2") == False

    clan = cm.data["clans"]["TestClan"]
    assert "player1" in clan["members"]
    assert clan["points"] == 0

def test_join_and_leave_clan(temp_clan_file):
    cm = ClanManager(temp_clan_file)
    cm.create_clan("TestClan", "player1")

    assert cm.join_clan("TestClan", "player2") == True
    assert cm.join_clan("NonExistent", "player3") == False

    clan = cm.data["clans"]["TestClan"]
    assert "player2" in clan["members"]

    assert cm.leave_clan("TestClan", "player2") == True
    clan = cm.data["clans"]["TestClan"]
    assert "player2" not in clan["members"]

def test_clan_disbands_when_empty(temp_clan_file):
    cm = ClanManager(temp_clan_file)
    cm.create_clan("SoloClan", "player1")
    assert cm.leave_clan("SoloClan", "player1") == True
    assert "SoloClan" not in cm.data["clans"]

def test_clan_quests(temp_clan_file):
    cm = ClanManager(temp_clan_file)
    cm.create_clan("QuestClan", "player1")

    assert cm.add_clan_quest("QuestClan", "Defeat 100 enemies", 100) == True
    quests = cm.get_clan_quests("QuestClan")
    assert len(quests) == 1
    assert quests[0]["description"] == "Defeat 100 enemies"

    assert cm.progress_clan_quest("QuestClan", 0, 50) == True
    quests = cm.get_clan_quests("QuestClan")
    assert quests[0]["current"] == 50
    assert quests[0]["completed"] == False

    assert cm.progress_clan_quest("QuestClan", 0, 60) == True
    quests = cm.get_clan_quests("QuestClan")
    assert quests[0]["current"] == 100
    assert quests[0]["completed"] == True
    assert cm.data["clans"]["QuestClan"]["points"] == 10

def test_clan_points_and_cosmetics(temp_clan_file):
    cm = ClanManager(temp_clan_file)
    cm.create_clan("WinClan", "p1")

    assert cm.add_clan_points("WinClan", 500) == True
    assert cm.data["clans"]["WinClan"]["points"] == 500

    assert cm.unlock_cosmetic("WinClan", "Tournament_Champion_Aura") == True
    assert "Tournament_Champion_Aura" in cm.data["clans"]["WinClan"]["cosmetics"]

    # unlock again shouldn't duplicate
    assert cm.unlock_cosmetic("WinClan", "Tournament_Champion_Aura") == False
    assert len(cm.data["clans"]["WinClan"]["cosmetics"]) == 1

def test_clan_leaderboard(temp_clan_file):
    cm = ClanManager(temp_clan_file)
    cm.create_clan("Clan1", "p1")
    cm.create_clan("Clan2", "p2")

    cm.data["clans"]["Clan1"]["points"] = 50
    cm.data["clans"]["Clan2"]["points"] = 100

    leaderboard = cm.get_clan_leaderboard()
    assert leaderboard[0]["name"] == "Clan2"
    assert leaderboard[0]["points"] == 100
    assert leaderboard[1]["name"] == "Clan1"
    assert leaderboard[1]["points"] == 50
