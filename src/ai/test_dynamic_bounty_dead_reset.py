from ai.game_modes import DynamicBountyMode

class MockEntity:
    def __init__(self, entity_id, kills=0):
        self.id = entity_id
        self.alive = True
        self.ball_type = "warrior"
        self.kills = kills
        self.x = 100.0
        self.y = 100.0
        self.is_dynamic_bounty = False
        self.score = 0
        self.team = f"Team_{entity_id}"

class MockWorld:
    def __init__(self):
        self.events = []
    def add_event(self, event_type, data):
        self.events.append((event_type, data))

def test_dynamic_bounty_resets_on_death():
    mode = DynamicBountyMode()
    world = MockWorld()

    b1 = MockEntity(1, kills=5)
    b2 = MockEntity(2, kills=0)

    # Tick 1: b1 gets the bounty
    mode.tick(world, [b1, b2], delta=0.5)
    assert b1.is_dynamic_bounty is True

    # Tick 2: b1 dies, b2 is alive but doesn't have kills/score to be bounty immediately
    b1.alive = False

    mode.tick(world, [b1, b2], delta=0.5)

    # The flag should be reset for b1 since it's dead
    assert b1.is_dynamic_bounty is False
