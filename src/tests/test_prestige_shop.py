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
