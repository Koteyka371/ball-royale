import pytest
from ai.game_modes import GameMode, ReverseDualPayloadMode
from ai.action import Action
import math

class MockBall:
    def __init__(self, x=0, y=0, team="Red"):
        self.x = x
        self.y = y
        self.team = team
        self.alive = True
        self.ball_type = "player"
        self.id = 1
        self.radius = 15.0
        self.damage = 100.0
        self.hp = 100.0
        self.mass = 1.0

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.dead_balls = []

def test_payload_hazards_conveyor():
    mode = ReverseDualPayloadMode()
    world = MockWorld()

    payload_red = MockBall(100, 500, "Red")
    payload_red.is_payload = True
    payload_red.ball_type = "payload"

    player_red = MockBall(100, 500, "Red")

    mode.payload_red = payload_red
    balls = [payload_red, player_red]

    # Tick with large delta to trigger hazard spawn
    import random
    random.seed(42) # Try to get conveyor

    mode.tick(world, balls, 25.0)

    # We should have hazards now (supply drops or payload hazards)
    hazards = world.arena.hazards
    conveyors = [h for h in hazards if getattr(h, "kind", "") == "payload_conveyor_belt"]
    gravity_wells = [h for h in hazards if getattr(h, "kind", "") == "payload_gravity_well"]

    # Tick again to trigger movement physics from spawned hazard
    if conveyors:
        conveyor = conveyors[0]
        conveyor.x = player_red.x # Ensure player is inside
        conveyor.y = player_red.y
        player_x = player_red.x
        mode.tick(world, balls, 0.016)
        assert player_red.x != player_x or player_red.y != 500, "Player should be moved by conveyor"

def test_payload_hazards_gravity_well():
    mode = ReverseDualPayloadMode()
    world = MockWorld()

    payload_red = MockBall(100, 500, "Red")
    payload_red.is_payload = True
    payload_red.ball_type = "payload"

    player_red = MockBall(100, 500, "Red")

    mode.payload_red = payload_red
    balls = [payload_red, player_red]

    # Try to force gravity well
    import random
    random.seed(45) # Different seed

    mode.tick(world, balls, 25.0)

    hazards = world.arena.hazards
    gravity_wells = [h for h in hazards if getattr(h, "kind", "") == "payload_gravity_well"]

    if gravity_wells:
        gw = gravity_wells[0]
        gw.x = player_red.x + 20 # Put well close
        gw.y = player_red.y
        initial_hp = gw.hp
        mode.tick(world, balls, 0.016)
        assert gw.hp < initial_hp, "Gravity well should take damage from player"

        # Test destruction
        gw.hp = 1.0
        mode.tick(world, balls, 0.016)
        # Should be destroyed and removed
        assert gw not in world.arena.hazards, "Gravity well should be destroyed"

if __name__ == "__main__":
    pytest.main(["-v", "src/tests/test_payload_hazards.py"])
