import pytest
from ai.game_modes import TickingPayloadMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, x=500, y=500, team="Neutral"):
        self.x = x
        self.y = y
        self.team = team
        self.ball_type = "normal"
        self.alive = True

def test_payload_cargo_type():
    mode = TickingPayloadMode()
    world = MockWorld()

    # Need to run setup first to initialize properly
    payload = MockBall(x=500.0, y=500.0, team="Neutral")
    payload.ball_type = "payload"
    # Red pusher is very close to the payload
    balls = [
        MockBall(x=600.0, y=500.0, team="Red"), # within 150 radius of payload (x=700)
        MockBall(x=100.0, y=500.0, team="Blue"), # far away
        payload
    ]

    mode.setup(world, balls)

    # Mock specific cargo type
    mode.payload.cargo_type = "healing_spring"

    assert len(world.arena.hazards) == 0

    # Manually trigger milestone crossing
    # Cross right: Red pushing
    mode.payload.x = 700.0
    mode.tick(world, balls)

    assert len(world.arena.hazards) >= 1
    # Check if the created hazard has the right kind
    found_healing_spring = False
    for h in world.arena.hazards:
        if getattr(h, "kind", "") == "healing_spring":
            found_healing_spring = True
            break

    assert found_healing_spring, f"Expected to find a 'healing_spring' hazard. Found: {[getattr(h, 'kind', '') for h in world.arena.hazards]}"
