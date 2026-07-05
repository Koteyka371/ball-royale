import re

with open("src/ai/test_game_modes.py", "r") as f:
    content = f.read()

# Add events list to MockWorld if it doesn't exist
new_mockworld = """class MockWorld:
    def __init__(self):
        self.arena = None
        self.dead_balls = []
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))"""

content = re.sub(
    r'class MockWorld:.*?pass',
    new_mockworld,
    content,
    flags=re.DOTALL
)

# Also check for simple `class MockWorld:`
content = content.replace(
    'class MockWorld:\n    pass',
    new_mockworld
)

with open("src/ai/test_game_modes.py", "w") as f:
    f.write(content)
