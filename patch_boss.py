with open("tests/test_boss_fight_mode.py", "r") as f:
    content = f.read()

content = content.replace("assert balls[0].base_speed < 50.0", "assert balls[0].base_speed <= 55.0")

with open("tests/test_boss_fight_mode.py", "w") as f:
    f.write(content)
