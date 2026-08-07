import pytest
import os
from system.clan import ClanManager

@pytest.fixture
def temp_clan_file(tmp_path):
    file_path = tmp_path / "test_clans.json"
    yield str(file_path)
    if os.path.exists(file_path):
        os.remove(file_path)

def test_form_and_break_alliance(temp_clan_file):
    cm = ClanManager(temp_clan_file)
    cm.create_clan("ClanA", "p1")
    cm.create_clan("ClanB", "p2")
    cm.create_clan("ClanC", "p3")
    cm.create_clan("ClanD", "p4")

    assert cm.form_alliance("ClanA", "ClanB") == True
    assert cm.form_alliance("ClanB", "ClanC") == True

    # Should not exceed 3 clans in a cluster
    assert cm.form_alliance("ClanC", "ClanD") == False

    # Already allied
    assert cm.form_alliance("ClanA", "ClanB") == False

    cluster = cm.get_alliance_cluster("ClanA")
    assert "ClanA" in cluster
    assert "ClanB" in cluster
    assert "ClanC" in cluster
    assert "ClanD" not in cluster

    assert cm.break_alliance("ClanB", "ClanC") == True

    cluster_a = cm.get_alliance_cluster("ClanA")
    assert "ClanC" not in cluster_a

def test_shared_territories(temp_clan_file):
    cm = ClanManager(temp_clan_file)
    cm.create_clan("ClanX", "p1")
    cm.create_clan("ClanY", "p2")

    cm.capture_territory("ClanX", "North_Base")
    cm.capture_territory("ClanY", "South_Base")

    assert cm.form_alliance("ClanX", "ClanY") == True

    shared = cm.get_shared_territories("ClanX")
    assert "North_Base" in shared
    assert "South_Base" in shared

def test_mega_quests_alliance_rewards(temp_clan_file):
    cm = ClanManager(temp_clan_file)
    cm.create_clan("Guild1", "p1")
    cm.create_clan("Guild2", "p2")

    cm.form_alliance("Guild1", "Guild2")

    rewards = [
        {"type": "buff", "value": "Alliance_Power"},
        {"type": "cosmetic", "value": "Mega_Quest_Cape"},
        {"type": "stash_item", "value": "diamond", "amount": 5}
    ]

    assert cm.add_mega_quest("Guild1", "Defeat 500 Bosses", 500, rewards=rewards) == True

    quests = cm.get_mega_quests("Guild1")
    assert len(quests) == 1

    # Progress quest to completion
    assert cm.progress_mega_quest("Guild1", 0, 500, "p1") == True

    quests_after = cm.get_mega_quests("Guild1")
    assert quests_after[0]["completed"] == True

    # Both clans should receive the rewards and the flat 50 points
    c1 = cm.data["clans"]["Guild1"]
    c2 = cm.data["clans"]["Guild2"]

    assert c1["points"] == 50
    assert c2["points"] == 50

    assert "Alliance_Power" in c1.get("buffs", [])
    assert "Alliance_Power" in c2.get("buffs", [])

    assert "Mega_Quest_Cape" in c1.get("cosmetics", [])
    assert "Mega_Quest_Cape" in c2.get("cosmetics", [])

    assert c1.get("stash", {}).get("diamond", 0) == 5
    assert c2.get("stash", {}).get("diamond", 0) == 5
