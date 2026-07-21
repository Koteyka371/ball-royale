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
    assert world.profile_manager.data["skill_points"] == 38
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
    system.tick(balls, [], 2)

    assert system.active_vote is None
    assert world.profile_manager.data["skill_points"] == 38
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
    assert world.profile_manager.data["skill_points"] == 38
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
    system.tick(balls, [], 2)

    assert system.votes["lava"] == 9999
    assert world.profile_manager.data["skill_points"] == 38
    events = [e[0] for e in world.events]
    assert "crowd_cheer" in events"""
content = content.replace(old_ext_skew, new_ext_skew)

# Update test_player_bribe_vote_cancel
old_player_cancel = """    # Should use skill_points first
    result = system.player_bribe_vote("player1", "cancel")
    assert result == True
    assert system.active_vote is None
    assert world.profile_manager.data["skill_points"] == 38
    assert world.profile_manager.data["prestige_tokens"] == 5
    events = [e[0] for e in world.events]
    assert "vote_cancelled" in events"""

new_player_cancel = """    # Should use skill_points first
    result = system.player_bribe_vote("player1", "cancel")
    assert result == True

    system.vote_auction_timer = 0
    system._resolve_vote_auction([])

    assert system.active_vote is None
    assert world.profile_manager.data["skill_points"] == 38
    assert world.profile_manager.data["prestige_tokens"] == 5
    events = [e[0] for e in world.events]
    assert "vote_cancelled" in events"""
content = content.replace(old_player_cancel, new_player_cancel)

# Update test_player_bribe_vote_skew
old_player_skew = """    result = system.player_bribe_vote("player2", "skew", "spike")
    assert result == True
    assert system.votes["spike"] == 5
    assert world.profile_manager.data["skill_points"] == 0
    assert world.profile_manager.data["prestige_tokens"] == 4
    events = [e[0] for e in world.events]
    assert "crowd_cheer" in events"""

new_player_skew = """    result = system.player_bribe_vote("player2", "skew", "spike")
    assert result == True

    system.vote_auction_timer = 0
    system._resolve_vote_auction([])

    assert system.votes["spike"] == 9999
    assert world.profile_manager.data["skill_points"] == 0
    assert world.profile_manager.data["prestige_tokens"] == 4
    events = [e[0] for e in world.events]
    assert "crowd_cheer" in events"""
content = content.replace(old_player_skew, new_player_skew)

with open("src/system/test_crowd_system.py", "w") as f:
    f.write(content)
