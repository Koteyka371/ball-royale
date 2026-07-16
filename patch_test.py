with open("src/ai/test_bumper_booster_void.py", "r") as f:
    content = f.read()

content = content.replace('void_panel = MockEntity(x=0, y=0, kind="void_panel", radius=50.0)', 'void_panel = MockEntity(x=0, y=0, kind="void_panel", radius=50.0, damage=0.0)')

with open("src/ai/test_bumper_booster_void.py", "w") as f:
    f.write(content)
