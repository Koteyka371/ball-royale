with open("tests/test_sonar_ping.py", "r") as f:
    content = f.read()

# Change smoke position so ball is not inside it.
content = content.replace("MockHazard(30.0, 0.0, \"smokescreen\")", "MockHazard(30.0, 0.0, \"smokescreen\"); smoke.radius = 20.0")

with open("tests/test_sonar_ping.py", "w") as f:
    f.write(content)
