with open("src/arena/procedural_arena.py", "r") as f:
    text = f.read()

text = text.replace(
    '"position_swap_booster"',
    '"position_swap_booster", "deployable_shockwave_mine"'
)

with open("src/arena/procedural_arena.py", "w") as f:
    f.write(text)
