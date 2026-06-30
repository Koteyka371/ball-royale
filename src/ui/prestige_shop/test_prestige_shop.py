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
