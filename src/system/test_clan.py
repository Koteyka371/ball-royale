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

def test_unlock_buff(temp_clan_file):
    cm = ClanManager(temp_clan_file)
    cm.create_clan("BuffClan", "p1")

    assert cm.unlock_buff("BuffClan", "Guild_Wide_Passive_Buff") == True
    assert "Guild_Wide_Passive_Buff" in cm.data["clans"]["BuffClan"]["buffs"]

    # unlock again shouldn't duplicate
    assert cm.unlock_buff("BuffClan", "Guild_Wide_Passive_Buff") == False
    assert len(cm.data["clans"]["BuffClan"]["buffs"]) == 1

def test_clan_perks(temp_clan_file):
    cm = ClanManager(temp_clan_file)
    cm.create_clan("PerkClan", "p1")

    # Add points
    cm.add_clan_points("PerkClan", 100)

    # Test unlocking without points (fails)
    assert cm.unlock_perk("PerkClan", "hp_boost_1", 150) == False

    # Test unlocking with enough points
    assert cm.unlock_perk("PerkClan", "hp_boost_1", 50) == True
    assert cm.data["clans"]["PerkClan"]["points"] == 50
    assert "hp_boost_1" in cm.get_clan_perks("PerkClan")

    # Test duplicate unlock (fails)
    assert cm.unlock_perk("PerkClan", "hp_boost_1", 10) == False
    assert cm.data["clans"]["PerkClan"]["points"] == 50

    # Test unlocking with missing requirement (fails)
    assert cm.unlock_perk("PerkClan", "hp_boost_3", 10, required_perk="hp_boost_2") == False

    # Test unlocking with met requirement
    assert cm.unlock_perk("PerkClan", "hp_boost_2", 10, required_perk="hp_boost_1") == True
    assert "hp_boost_2" in cm.get_clan_perks("PerkClan")
    assert cm.data["clans"]["PerkClan"]["points"] == 40

def test_clan_hub_decorations(temp_clan_file):
    cm = ClanManager(temp_clan_file)
    cm.create_clan("DecoClan", "p1")

    # Unlock a decoration
    assert cm.unlock_decoration("DecoClan", "Champion_Trophy") == True
    assert "Champion_Trophy" in cm.data["clans"]["DecoClan"]["decorations"]

    # Unlock duplicate shouldn't duplicate
    assert cm.unlock_decoration("DecoClan", "Champion_Trophy") == False
    assert len(cm.data["clans"]["DecoClan"]["decorations"]) == 1

    # Cannot place unowned decoration
    assert cm.place_decoration("DecoClan", "Speed_Statue", 10, 20) == False

    # Place owned decoration
    assert cm.place_decoration("DecoClan", "Champion_Trophy", 10, 20) == True
    assert len(cm.data["clans"]["DecoClan"]["hub"]) == 1
    assert cm.data["clans"]["DecoClan"]["hub"][0]["decoration"] == "Champion_Trophy"

    # Placing it again elsewhere moves it (or overwrites at that pos, our implementation replaces at same pos but doesn't limit qty, but let's just place another)
    assert cm.place_decoration("DecoClan", "Champion_Trophy", 30, 40) == True
    assert len(cm.data["clans"]["DecoClan"]["hub"]) == 2

    # Remove decoration
    assert cm.remove_decoration("DecoClan", 10, 20) == True
    assert len(cm.data["clans"]["DecoClan"]["hub"]) == 1

    # Check buffs
    buffs = cm.get_hub_buffs("DecoClan")
    assert "Tournament_Champion_Aura" in buffs


def test_clan_tournament(temp_clan_file):
    cm = ClanManager(temp_clan_file)
    cm.create_clan("ChampClan", "p1")
    cm.create_clan("RunnerUpClan", "p2")
    cm.create_clan("Top10Clan", "p3")
    cm.create_clan("LoserClan", "p4")

    assert cm.register_for_tournament("ChampClan", "tourney_1") == True
    assert cm.register_for_tournament("RunnerUpClan", "tourney_1") == True
    assert cm.register_for_tournament("Top10Clan", "tourney_1") == True
    assert cm.register_for_tournament("LoserClan", "tourney_1") == True

    rankings = [
        {"clan_name": "ChampClan", "points": 1000},
        {"clan_name": "RunnerUpClan", "points": 800},
        {"clan_name": "Top10Clan", "points": 500},
        {"clan_name": "LoserClan", "points": 100}
    ]

    assert cm.process_tournament_results("tourney_1", rankings) == True

    # Check top 3 rewards
    champ = cm.data["clans"]["ChampClan"]
    assert champ["points"] == 1000
    assert "Tournament_Champion" in champ.get("cosmetics", [])
    assert "Currency_Boost_Weekly" in champ.get("buffs", [])

    top10 = cm.data["clans"]["Top10Clan"]
    assert top10["points"] == 500
    assert "Tournament_Champion" in top10.get("cosmetics", [])
    assert "Currency_Boost_Weekly" in top10.get("buffs", [])

    # Check outside top 3
    loser = cm.data["clans"]["LoserClan"]
    assert loser["points"] == 100
    assert "Tournament_Champion" not in loser.get("cosmetics", [])
    assert "Currency_Boost_Weekly" not in loser.get("buffs", [])
