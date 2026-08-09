import pytest
import os
from system.profile import ProfileManager

def test_recolor_skin():
    filename = "test_profile_recolor.json"
    if os.path.exists(filename):
        os.remove(filename)

    profile = ProfileManager(filename=filename)
    profile.data["inventory"] = {"materials": {"Red Dye": 1, "Blue Dye": 1}, "crafted_items": {}}
    profile.data["unlocked_balls"] = ["default", "skin_ninja"]
    profile.save()

    # Needs to implement this function
    assert profile.craft_recolor("skin_ninja", "Red Dye") == True
    assert profile.data["inventory"]["materials"]["Red Dye"] == 0
    assert "skin_ninja_Red Dye" in profile.data["unlocked_balls"]

    # Test equipping it
    assert profile.equip_skin("skin_ninja_Red Dye") == True
    assert profile.data["equipped_skin"] == "skin_ninja_Red Dye"

    # Test failure missing material
    assert profile.craft_recolor("skin_ninja", "Red Dye") == False

    # Test failure missing base skin
    assert profile.craft_recolor("skin_dragon", "Blue Dye") == False

    # Can recolor base default skin
    assert profile.craft_recolor("default", "Blue Dye") == True
    assert "default_Blue Dye" in profile.data["unlocked_balls"]
    assert profile.data["inventory"]["materials"]["Blue Dye"] == 0

    if os.path.exists(filename):
        os.remove(filename)
