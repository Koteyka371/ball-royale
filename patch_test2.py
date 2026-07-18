with open("src/tests/test_bone_wall.py", "r") as f:
    content = f.read()

# Since projectile doesn't touch the wall, we need to push it into the wall. The wall x is 60.0. The projectile starts at 60.0, but Action.execute handles hazard clamping only if the hazard is within radius.
# A projectile at x=60, y=0 and wall at x=60, y=0. Wait, dist=0. "dist > 0" is a condition in the breakable wall logic. Let's make the projectile start slightly offset.

content = content.replace("proj = MockBall(3, wall.x, wall.y, \"team2\")", "proj = MockBall(3, wall.x - 5, wall.y, \"team2\")")

with open("src/tests/test_bone_wall.py", "w") as f:
    f.write(content)
