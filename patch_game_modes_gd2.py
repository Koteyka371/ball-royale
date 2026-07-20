with open("src/ai/game_modes.gd", "r") as f:
    content = f.read()

# Fix the formatting issue where it got appended directly to the end of a line
target = 'GAME_MODES["zero_gravity_meteor_shower"] = ZeroGravityMeteorShowerMode.new()class CursedBoosterMode extends GameMode:'
replace = 'GAME_MODES["zero_gravity_meteor_shower"] = ZeroGravityMeteorShowerMode.new()\n\nclass CursedBoosterMode extends GameMode:'
content = content.replace(target, replace)

with open("src/ai/game_modes.gd", "w") as f:
    f.write(content)
