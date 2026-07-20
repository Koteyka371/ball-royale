from system.crowd_system import CrowdSystem

class MockArena:
    def __init__(self):
        self.temperature = 20.0

class MockWorld:
    def __init__(self):
        self.events = []
        self.arena = MockArena()
        self.active_mode = None

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, id, hp, max_hp, kills, ball_type="player"):
        self.id = id
        self.hp = hp
        self.max_hp = max_hp
        self.kills = kills
        self.ball_type = ball_type
        self.alive = True
        self.x = 0.0
        self.y = 0.0
        self.score = 0
        self.xp = 0

def test_bounty_command_and_claim():
    world = MockWorld()
    system = CrowdSystem(world)

    b1 = MockBall(1, 100, 100, 0, "tank")
    b2 = MockBall(2, 100, 100, 0, "speedster")
    balls = [b1, b2]

    # Test placing bounty
    system.queue_external_command("User1", "!bounty 2")
    system.tick(balls, [], 1)

    # Timer should be set
    assert getattr(b2, "crowd_bounty_timer", 0) > 0

    # Visual effect and cheer should be added
    events = [e[0] for e in world.events]
    assert "visual_effect" in events
    bounty_marks = [e for e in world.events if e[0] == "visual_effect" and e[1].get("type") == "bounty_mark"]
    assert len(bounty_marks) > 0
    assert bounty_marks[0][1]["target_id"] == 2

    # Simulate tick decrement
    old_timer = b2.crowd_bounty_timer
    system.tick(balls, [], 2)
    assert b2.crowd_bounty_timer == old_timer - 1

    # Simulate kill
    world.events = []
    kill_log = [{"killer_id": 1, "victim_id": 2, "tick": 3}]

    # We need to manually call tick to process kill log (which is processed inside _check_events inside tick)
    system.tick(balls, kill_log, 3)

    # Check rewards
    assert b1.score >= 1000
    assert b1.xp >= 500

    # Check visual effect and cheer
    bounty_claims = [e for e in world.events if e[0] == "visual_effect" and e[1].get("type") == "bounty_claimed"]
    assert len(bounty_claims) > 0
    assert bounty_claims[0][1]["target_id"] == 1
