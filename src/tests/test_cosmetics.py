from system.profile import ProfileManager

def test_equip_skin():
    pm = ProfileManager("test_profile.json")
    # Reset file
    pm.data = {}
    pm.save()

    # default should be equippable
    assert pm.equip_skin("default") == True
    assert pm.data["equipped_skin"] == "default"

    # can't equip what we don't own
    assert pm.equip_skin("ninja") == False

    # add to cosmetics
    pm.add_cosmetic("ninja")
    assert pm.equip_skin("ninja") == True
    assert pm.data["equipped_skin"] == "ninja"

    # add via upgrade
    pm.data["prestige_upgrades"] = {"skin_neon": 1}
    assert pm.equip_skin("neon") == True
    assert pm.data["equipped_skin"] == "neon"

if __name__ == "__main__":
    test_equip_skin()
    print("Tests passed!")
