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

def test_clan_roles_and_stash(temp_clan_file):
    cm = ClanManager(temp_clan_file)
    cm.create_clan("TradeClan", "leader1")
    cm.join_clan("TradeClan", "member1")

    # Check default roles
    clan = cm.data["clans"]["TradeClan"]
    assert clan["roles"]["leader1"] == "leader"
    assert clan["roles"]["member1"] == "member"

    # Leader promotes member
    assert cm.set_member_role("TradeClan", "leader1", "member1", "officer") == True
    assert clan["roles"]["member1"] == "officer"

    # Member tries to promote (fails)
    assert cm.set_member_role("TradeClan", "member1", "leader1", "member") == False

    # Deposit items (anyone)
    assert cm.deposit_to_stash("TradeClan", "member1", "wood", 50) == True
    assert cm.deposit_to_stash("TradeClan", "leader1", "iron", 10) == True
    assert clan["stash"]["wood"] == 50
    assert clan["stash"]["iron"] == 10

    # Demote member to regular member
    assert cm.set_member_role("TradeClan", "leader1", "member1", "member") == True

    # Member tries to withdraw (fails)
    assert cm.withdraw_from_stash("TradeClan", "member1", "wood", 10) == False

    # Leader withdraws
    assert cm.withdraw_from_stash("TradeClan", "leader1", "wood", 20) == True
    assert clan["stash"]["wood"] == 30

    # Promote member to officer and withdraw
    assert cm.set_member_role("TradeClan", "leader1", "member1", "officer") == True
    assert cm.withdraw_from_stash("TradeClan", "member1", "wood", 30) == True

    # Stash should not have 'wood' anymore
    assert "wood" not in clan["stash"]
