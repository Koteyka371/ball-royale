with open("src/ai/game_modes.gd", "r") as f:
    content = f.read()

content = content.replace("world.projectiles.remove_at(found_idx)", "world.projectiles.erase(p)")
content = content.replace("world.arena.hazards.remove_at(h_idx)", "world.arena.hazards.erase(h)")

with open("src/ai/game_modes.gd", "w") as f:
    f.write(content)
