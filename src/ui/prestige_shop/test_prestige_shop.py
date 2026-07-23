from system.profile import ProfileManager
from ui.prestige_shop.prestige_shop import PrestigeShop
import os
import json

def test_prestige_shop_available_upgrades():
    shop = PrestigeShop(None)
    upgrades = shop.get_available_upgrades()
    assert "mutator_unlocked" in upgrades
    assert "unlock_time_mage" in upgrades
    assert upgrades["unlock_time_mage"]["cost"] == 25

def test_prestige_shop_buy_upgrade():
    test_file = "test_profile_shop.json"
    with open(test_file, 'w') as f:
        json.dump({"prestige_tokens": 50, "prestige_upgrades": {}}, f)

    pm = ProfileManager(test_file)
    shop = PrestigeShop(pm)

    # Buy a valid upgrade
    success = shop.buy_upgrade("unlock_time_mage")
    assert success is True
    assert pm.data["prestige_tokens"] == 25
    assert pm.data["prestige_upgrades"].get("unlock_time_mage", 0) == 1

    # Buy an invalid upgrade
    success = shop.buy_upgrade("invalid_upgrade")
    assert success is False
    assert pm.data["prestige_tokens"] == 25

    if os.path.exists(test_file):
        os.remove(test_file)

def test_prestige_shop_play_roulette():
    test_file = "test_profile_shop_roulette.json"
    with open(test_file, 'w') as f:
        json.dump({"prestige_tokens": 100, "skill_points": 0, "cosmetics": []}, f)

    pm = ProfileManager(test_file)
    shop = PrestigeShop(pm)

    # Mock random to return 1 (which should be "red" since 1%2 != 0)
    import random
    original_randint = random.randint
    random.randint = lambda a, b: 1

    try:
        # Test winning bet
        success, msg = shop.play_roulette(10, "color", "red")
        assert success is True
        assert "You won 20 tokens!" in msg
        assert pm.data["prestige_tokens"] == 110 # 100 - 10 + 20

        # Test losing bet
        success, msg = shop.play_roulette(10, "color", "black")
        assert success is True
        assert "You lost your bet." in msg
        assert pm.data["prestige_tokens"] == 100 # 110 - 10

        # Test not enough tokens
        success, msg = shop.play_roulette(200, "color", "red")
        assert success is False
        assert "Not enough tokens" in msg
        assert pm.data["prestige_tokens"] == 100

        # Test cosmetic unlock on large win
        # Force a large win
        random.randint = lambda a, b: 0 # green

        # Mock random.random to return 0.0 (guarantees < 0.1)
        original_random = random.random
        random.random = lambda: 0.0

        success, msg = shop.play_roulette(10, "color", "green")
        assert success is True
        assert "You won 350 tokens!" in msg
        assert "Also won exclusive cosmetic: roulette_master!" in msg
        assert pm.data["prestige_tokens"] == 440 # 100 - 10 + 350
        assert "roulette_master" in pm.data["cosmetics"]

        random.random = original_random

    finally:
        random.randint = original_randint

    if os.path.exists(test_file):
        os.remove(test_file)


def test_prestige_shop_spin_wheel():
    test_file = "test_profile_shop_wheel.json"
    with open(test_file, 'w') as f:
        json.dump({"prestige_tokens": 1, "skill_points": 0}, f)

    pm = ProfileManager(test_file)
    shop = PrestigeShop(pm)

    # Mock random to always return 0 (should select the first reward: skill_points_10)
    import random
    original_uniform = random.uniform
    random.uniform = lambda a, b: 0

    try:
        success, msg = shop.spin_wheel(cost=1)
        assert success is True
        assert "Won 10 Skill Points" in msg
        assert pm.data["prestige_tokens"] == 0

        # Test not enough tokens
        success, msg = shop.spin_wheel(cost=1)
        assert success is False
        assert "Not enough tokens" in msg

    finally:
        random.uniform = original_uniform

    if os.path.exists(test_file):
        os.remove(test_file)
