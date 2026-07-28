import pytest
from system.guild import GuildManager
from ai.game_modes import GameMode, GuildWarMode

def test_guild_war_mode():
    import os
    if os.path.exists("guilds.json"):
        os.remove("guilds.json")
    gm = GuildManager()
    gm.create_guild("Attacker", "p1")
    gm.create_guild("Defender", "p2")
    gm.data["guilds"]["Defender"]["resources"] = 1000
    gm.build_hq_defense("Defender", "turret", 100, amount=3)

    mode = GuildWarMode("Attacker", "Defender")
    class DummyArena:
        def __init__(self):
            self.hazards = []
    class DummyWorld:
        def __init__(self):
            self.arena = DummyArena()
            self.balls = []
        def add_event(self, *args, **kwargs): pass

    world = DummyWorld()
    mode.setup(world, [])
    assert len(world.arena.hazards) == 3
    assert world.arena.hazards[0]["kind"] == "turret"
    assert world.arena.hazards[0]["is_defense"] == True

    # Test taking damage
    class DummyBall:
        def __init__(self, id, x, y):
            self.id = id
            self.x = x
            self.y = y
            self.hp = 100
            self.radius = 10
            self.alive = True
            self.ball_type = "player"

    b1 = DummyBall(1, 400, 300)
    world.balls = [b1, DummyBall(2, 0, 0)]
    mode.attacker_balls = [1]
    mode.defender_balls = [2]

    # Tick to take damage
    mode.tick(world, world.balls, 0.1)

    assert mode.hq_hp < 5000
