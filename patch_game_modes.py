with open("src/ai/game_modes.py", "r") as f:
    content = f.read()

# Replace booster_kinds definition if cleanse_booster not in it
if "cleanse_booster" not in content:
    content = content.replace(
        'booster_kinds = ["speed_booster", "damage_booster", "hp_booster", "vision_booster", "stamina_booster", "pull_booster", "nemesis_booster", "nemesis_compass_item", "shadow_booster", "weather_scanner_item", "aura_booster", "emp_immunity_booster"]',
        'booster_kinds = ["speed_booster", "damage_booster", "hp_booster", "vision_booster", "stamina_booster", "pull_booster", "nemesis_booster", "nemesis_compass_item", "shadow_booster", "weather_scanner_item", "aura_booster", "emp_immunity_booster", "cleanse_booster"]'
    )
    with open("src/ai/game_modes.py", "w") as f:
        f.write(content)
    print("Patched game_modes.py")
else:
    print("cleanse_booster already in game_modes.py")

with open("src/ai/game_modes.gd", "r") as f:
    gd_content = f.read()

if "cleanse_booster" not in gd_content:
    gd_content = gd_content.replace(
        'var booster_kinds = ["speed_booster", "damage_booster", "hp_booster", "vision_booster", "stamina_booster", "pull_booster", "nemesis_booster", "nemesis_compass_item", "shadow_booster", "weather_scanner_item", "aura_booster", "emp_immunity_booster"]',
        'var booster_kinds = ["speed_booster", "damage_booster", "hp_booster", "vision_booster", "stamina_booster", "pull_booster", "nemesis_booster", "nemesis_compass_item", "shadow_booster", "weather_scanner_item", "aura_booster", "emp_immunity_booster", "cleanse_booster"]'
    )
    with open("src/ai/game_modes.gd", "w") as f:
        f.write(gd_content)
    print("Patched game_modes.gd")
else:
    print("cleanse_booster already in game_modes.gd")
