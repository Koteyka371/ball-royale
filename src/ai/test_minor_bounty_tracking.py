from ai.action import Action
from ai.ball_types_bounty_hunter import BountyHunter

class MockEntity:
    def __init__(self, id, x, y, alive=True, ball_type="normal", is_bounty=False, is_minor_bounty=False):
        self.id = id
        self.x = x
        self.y = y
        self.alive = alive
        self.ball_type = ball_type
        self.is_bounty = is_bounty
        self.is_minor_bounty = is_minor_bounty
        self.high_threat = False
        self.is_bounty_target = False
        self.is_bounty_contract_target = False

class MockWorld:
    def __init__(self):
        self.balls = []
        self.events = []

def test_bounty_hunter_tracks_minor_bounty():
    world = MockWorld()
    hunter = MockEntity(id=1, x=0, y=0, ball_type="bounty_hunter")
    # Not a target
    normal = MockEntity(id=2, x=100, y=0)
    # Target
    target = MockEntity(id=3, x=200, y=0, is_minor_bounty=True)

    world.balls = [hunter, normal, target]

    action = Action(hunter, world)
    # The indicator updates every 2.0 seconds. Initialize timer to 0 to trigger it
    hunter.bounty_indicator_timer = 0.0
    action.execute("idle", 0.1)

    # Verify that the bounty compass event was emitted for the minor bounty target
    compass_events = [e for e in world.events if e["type"] == "bounty_compass"]
    assert len(compass_events) == 1
    assert compass_events[0]["data"]["target_x"] == 200
    assert compass_events[0]["data"]["owner_id"] == 1
