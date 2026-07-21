import re

with open("src/system/test_crowd_system.py", "r") as f:
    content = f.read()

# Replace test_external_command_bribe_cancel completely
old_ext_cancel = """def test_external_command_bribe_cancel():
    world = MockWorld()
    system = CrowdSystem(world)
    balls = []

    system.active_vote = {"type": "spawn_hazard", "options": ["lava", "spike"]}
    system.votes = {"lava": 0, "spike": 0}
    system.vote_timer = 100

    system.queue_external_command("TwitchUser", "!bribe cancel")
    system.tick(balls, [], 1)

    assert system.active_vote is None
    events = [e[0] for e in world.events]
    assert "vote_cancelled" in events"""

new_ext_cancel = """def test_external_command_bribe_cancel():
    world = MockWorld()
    system = CrowdSystem(world)
    balls = []

    system.active_vote = {"type": "spawn_hazard", "options": ["lava", "spike"]}
    system.votes = {"lava": 0, "spike": 0}
    system.vote_timer = 100

    system.queue_external_command("TwitchUser", "!bribe cancel")
    system.tick(balls, [], 1)

    # Fast forward auction timer
    system.vote_auction_timer = 0
    system._resolve_vote_auction([])

    assert system.active_vote is None
    events = [e[0] for e in world.events]
    assert "vote_cancelled" in events"""
content = content.replace(old_ext_cancel, new_ext_cancel)

old_ext_skew = """def test_external_command_bribe_skew():
    world = MockWorld()
    system = CrowdSystem(world)
    balls = []

    system.active_vote = {"type": "spawn_hazard", "options": ["lava", "spike"]}
    system.votes = {"lava": 0, "spike": 0}
    system.vote_timer = 100

    system.queue_external_command("TwitchUser", "!bribe skew lava")
    system.tick(balls, [], 1)

    assert system.votes["lava"] == 5
    events = [e[0] for e in world.events]
    assert "crowd_cheer" in events"""

new_ext_skew = """def test_external_command_bribe_skew():
    world = MockWorld()
    system = CrowdSystem(world)
    balls = []

    system.active_vote = {"type": "spawn_hazard", "options": ["lava", "spike"]}
    system.votes = {"lava": 0, "spike": 0}
    system.vote_timer = 100

    system.queue_external_command("TwitchUser", "!bribe skew lava")
    system.tick(balls, [], 1)

    # Fast forward auction timer
    system.vote_auction_timer = 0
    system._resolve_vote_auction([])

    assert system.votes["lava"] == 9999
    events = [e[0] for e in world.events]
    assert "crowd_cheer" in events"""
content = content.replace(old_ext_skew, new_ext_skew)

with open("src/system/test_crowd_system.py", "w") as f:
    f.write(content)
