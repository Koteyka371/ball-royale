with open("src/ai/action.py", "r") as f:
    text = f.read()

text = text.replace(
    '"position_swap_booster",',
    '"position_swap_booster", "deployable_shockwave_mine", "shockwave_mine",'
)

with open("src/ai/action.py", "w") as f:
    f.write(text)
