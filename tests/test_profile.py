from system.profile import ProfileManager
import os

def test_profile():
    if os.path.exists("test_profile.json"):
        os.remove("test_profile.json")

    pm = ProfileManager("test_profile.json")
    assert pm.data["skill_points"] == 0
    assert pm.data["unlocked_balls"] == ["basic"]

    pm.add_skill_points(10)
    assert pm.data["skill_points"] == 10

    assert pm.unlock_ball("sniper", 5)
    assert pm.data["skill_points"] == 5
    assert "sniper" in pm.data["unlocked_balls"]

    assert not pm.unlock_ball("ninja", 10)

    assert pm.upgrade_bonus("bonus_hp", 3)
    assert pm.data["skill_points"] == 2
    assert pm.data["bonuses"]["bonus_hp"] == 1


    # Test Quests
    quests = pm.get_daily_quests()
    assert len(quests) == 3

    # Progress a quest
    first_quest_type = quests[0]["type"]
    pm.update_quest_progress(first_quest_type, quests[0]["target"])

    quests_updated = pm.get_daily_quests()
    assert quests_updated[0]["completed"]
    # Initial was 2, but when completed it adds the reward skill points
    assert pm.data["skill_points"] == 2 + quests_updated[0]["reward"]

    if os.path.exists("test_profile.json"):
        os.remove("test_profile.json")

    print("All tests passed.")

if __name__ == "__main__":
    test_profile()
