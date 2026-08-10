import pytest
from unittest.mock import MagicMock
from ai.action import Action

def test_minion_summoner_booster():
    world = MagicMock()
    world.next_id = 100
    world.balls = []

    class Ball:
        pass
    ball = Ball()
    ball.id = 1
    ball.x = 100.0
    ball.y = 100.0
    ball.radius = 20.0
    ball.mass = 10.0
    ball.max_hp = 100.0
    ball.alive = True
    # Explicitly set mock attributes to their default values for numeric types.
    ball.minion_summoner_timer = 0.0
    ball.minion_summoner_spawned = False

    world.balls.append(ball)

    booster = MagicMock()
    # It must be a dictionary or have the attribute
    booster.get.side_effect = lambda key, default=None: getattr(booster, key, default)
    booster.kind = "minion_summoner_item"
    booster.x = 100.0
    booster.y = 100.0
    booster.radius = 10.0
    booster.active = True

    world.boosters = [booster]
    world.arena.hazards = []
    world.arena.safe_zone_center = (500.0, 500.0)
    world.arena.safe_zone_radius = 500.0
    world.arena.width = 1000.0
    world.arena.height = 1000.0
    world.arena.clamp_position.return_value = (100.0, 100.0, False)

    action = Action(ball, world)

    # Simulate booster collection
    action._collect_booster(0.1)

    assert ball.minion_summoner_timer == 15.0
    assert ball.minion_summoner_spawned == False
    assert booster.active == False

    # Simulate first tick (spawning minions)
    action.execute("idle", 0.1)

    assert ball.minion_summoner_spawned == True
    assert len(world.balls) == 4 # Original ball + 3 minions

    minions = [b for b in world.balls if b != ball]
    for minion in minions:
        assert minion.owner_id == ball.id
        assert minion.is_decoy == True
        assert minion.tether_target == ball.id
        assert minion.minion_summoner_lifetime == 15.0
        assert minion.radius == ball.radius * 0.5
        assert minion.mass == ball.mass * 0.5

    # Simulate lifetime expiring
    minion = minions[0]
    minion.minion_summoner_lifetime = 15.0
    minion.decoy_type = ""
    minion.decoy_timer = 0.0
    minion_action = Action(minion, world)
    minion_action.execute("idle", 15.0)
    assert minion.alive == False
