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

    pm.add_quest("Survive for 5 minutes", 50)
    quests = pm.get_quests()
    assert len(quests) == 1
    assert quests[0]["description"] == "Survive for 5 minutes"
    assert quests[0]["reward"] == 50
    assert not quests[0]["completed"]

    assert pm.complete_quest(0)
    assert pm.get_quests()[0]["completed"]
    assert pm.data["skill_points"] == 52

    assert not pm.complete_quest(0) # Already completed
    assert not pm.complete_quest(99) # Invalid index


    if os.path.exists("test_profile.json"):
        os.remove("test_profile.json")

    print("All tests passed.")

if __name__ == "__main__":
    test_profile()
