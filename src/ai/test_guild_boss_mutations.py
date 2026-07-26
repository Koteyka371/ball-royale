import pytest
from src.ai.game_modes import GuildBossFightMode
from src.ai.test_guild_boss_mode import MockWorld, MockBallGuildBoss

def test_guild_boss_tier_2_mutation():
    mode = GuildBossFightMode(tier=2)
    world = MockWorld()
    boss = MockBallGuildBoss(1, 0, 0)
    mode.setup(world, [boss])

    assert getattr(boss, "damage_reflection_active", False) == True
    assert getattr(boss, "damage_reflection_multiplier", 0.0) == 0.1

def test_guild_boss_tier_3_mutation():
    mode = GuildBossFightMode(tier=3)
    world = MockWorld()
    boss = MockBallGuildBoss(1, 0, 0)
    mode.setup(world, [boss])

    balls = [boss]
    assert len(balls) == 1

    # Tick past minion timer (starts at 5.0)
    mode.tick(world, balls, 5.1)

    # Boss + 1 minion
    assert len(balls) == 2

    minion = balls[-1]
    assert minion.ball_type == "minion"
    assert minion.team == "Boss"

if __name__ == "__main__":
    pytest.main(["-v", "test_guild_boss_mutations.py"])
