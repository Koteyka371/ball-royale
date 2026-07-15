import re

with open("src/ai/test_extreme_weather.py", "r") as f:
    content = f.read()

# Replace MockBall instantiation to correctly set properties for b1, b2, b3
# MockBall might not accept arbitrary kwargs in this file, we should just assign them

fix_replace = """    # Metal ball
    b1 = MockBall()
    b1.ball_type = "metal_drone"
    b1.hp = 100.0
    b1.max_hp = 100.0
    b1.x = 100.0
    b1.y = 100.0
    b1.radius = 10.0

    # Non-metal ball
    b2 = MockBall()
    b2.ball_type = "basic"
    b2.hp = 100.0
    b2.max_hp = 100.0
    b2.x = 300.0
    b2.y = 300.0
    b2.radius = 10.0

    # Ball with hazmat suit
    b3 = MockBall()
    b3.ball_type = "metal_drone"
    b3.hp = 100.0
    b3.max_hp = 100.0
    b3.hazmat_booster_timer = 10.0
    b3.x = 500.0
    b3.y = 500.0
    b3.radius = 10.0"""

search_str = """    # Metal ball
    b1 = MockBall(ball_type="metal_drone", hp=100.0, max_hp=100.0, x=100.0, y=100.0, radius=10.0)
    # Non-metal ball
    b2 = MockBall(ball_type="basic", hp=100.0, max_hp=100.0, x=300.0, y=300.0, radius=10.0)
    # Ball with hazmat suit
    b3 = MockBall(ball_type="metal_drone", hp=100.0, max_hp=100.0, hazmat_booster_timer=10.0, x=500.0, y=500.0, radius=10.0)"""

content = content.replace(search_str, fix_replace)

with open("src/ai/test_extreme_weather.py", "w") as f:
    f.write(content)
