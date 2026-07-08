with open("src/ai/test_damage_link_booster.py", "r") as f:
    content = f.read()

# Make FakeBall have ball_type = 'basic' and diff teams properly to be recognized as enemy
content = content.replace('enemy = FakeBall(50.0, 0.0)\n    enemy.team = "enemy"', 'enemy = FakeBall(50.0, 0.0)\n    enemy.team = "enemy"\n    enemy.ball_type = "basic2"')

with open("src/ai/test_damage_link_booster.py", "w") as f:
    f.write(content)
