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


def test_prestige_tokens():
    if os.path.exists("test_profile_tokens.json"):
        os.remove("test_profile_tokens.json")

    pm = ProfileManager("test_profile_tokens.json")
    # Setup for prestige
    pm.data["unlocked_balls"] = ["ball" + str(i) for i in range(34)]
    pm.data["bonuses"] = {"bonus_hp": 10, "bonus_speed": 10, "bonus_damage": 10}
    pm.data["skill_points"] = 500
    pm.save()

    assert pm.can_prestige()
    assert pm.do_prestige()

    # 5 + 1 + 500 // 100 = 11 tokens
    assert pm.data["prestige_tokens"] == 11
    assert pm.data["prestige_level"] == 1

    # Buy an upgrade
    assert pm.buy_prestige_upgrade("permanent_hp", 5)
    assert pm.data["prestige_tokens"] == 6
    assert pm.data["prestige_upgrades"]["permanent_hp"] == 1

    # Can't afford
    assert not pm.buy_prestige_upgrade("permanent_speed", 10)

    if os.path.exists("test_profile_tokens.json"):
        os.remove("test_profile_tokens.json")


def test_daily_login():
    import os
    if os.path.exists("test_profile_daily.json"):
        os.remove("test_profile_daily.json")

    pm = ProfileManager("test_profile_daily.json")

    # Day 1: New login (2023-10-01 is a Sunday, weekend -> x2 points)
    rewards = pm.process_daily_login("2023-10-01")
    assert rewards["skill_points"] == 20
    assert pm.data["login_streak"] == 1
    assert pm.data["skill_points"] == 20

    # Same day login: Should do nothing
    rewards2 = pm.process_daily_login("2023-10-01")
    assert rewards2 == {}
    assert pm.data["login_streak"] == 1
    assert pm.data["skill_points"] == 20

    # Day 2: Consecutive login (2023-10-02 is Monday -> x1 points)
    rewards3 = pm.process_daily_login("2023-10-02")
    assert rewards3["skill_points"] == 20
    assert pm.data["login_streak"] == 2
    assert pm.data["skill_points"] == 40

    # Day 4: Skip a day, streak resets (2023-10-04 is Wednesday -> x1 points)
    rewards4 = pm.process_daily_login("2023-10-04")
    assert rewards4["skill_points"] == 10
    assert pm.data["login_streak"] == 1

    # Force streak to 6 and simulate Day 5 login to hit 7
    # 2023-10-06 is Friday -> x1 points
    pm.data["login_streak"] = 6
    pm.data["last_login_date"] = "2023-10-05"
    rewards5 = pm.process_daily_login("2023-10-06")

    assert pm.data["login_streak"] == 7
    assert rewards5["skill_points"] == 70
    assert rewards5["prestige_tokens"] == 1
    assert rewards5["cosmetics"] == "streak_master_7"
    assert pm.data["prestige_tokens"] == 1
    assert "streak_master_7" in pm.data["cosmetics"]

    if os.path.exists("test_profile_daily.json"):
        os.remove("test_profile_daily.json")

if __name__ == "__main__":
    test_profile()
    test_prestige_tokens()
    test_daily_login()
