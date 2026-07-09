from ai.game_modes import GameMode

class MockBall:
    def __init__(self, id, level=1, color=None, x=500.0, y=500.0):
        self.id = id
        self.alive = True
        self.ball_type = "player"
        self.level = level
        self.x = x
        self.y = y
        self.radius = 15.0
        self.hp = 100.0
        if color:
            self.cosmetic_aura_color = color

    def take_damage(self, dmg):
        self.hp -= dmg

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

def test_aura_explosion():
    mode = GameMode()
    world = MockWorld()

    # Create two high level balls with red aura
    b1 = MockBall("b1", level=3, color=(1.0, 0.0, 0.0, 1.0), x=500.0, y=500.0)
    b2 = MockBall("b2", level=3, color=(1.0, 0.0, 0.0, 1.0), x=505.0, y=500.0)

    # Create a bystander
    b3 = MockBall("b3", level=1, color=None, x=510.0, y=510.0)

    # Add a ball far away
    b4 = MockBall("b4", level=1, color=None, x=900.0, y=900.0)

    balls = [b1, b2, b3, b4]

    mode.tick(world, balls, 0.016)

    # Check cooldowns
    assert getattr(b1, "aura_explosion_cooldown", 0.0) > 0.0
    assert getattr(b2, "aura_explosion_cooldown", 0.0) > 0.0

    # Check bystander got hit
    assert b3.hp < 100.0
    assert getattr(b3, "burn_timer", 0.0) > 0.0

    # Far ball shouldn't be hit
    assert b4.hp == 100.0

    # Check event
    assert len(world.events) > 0
    assert world.events[0][0] == "aura_elemental_explosion"
    assert world.events[0][1]["element"] == "fire"

if __name__ == "__main__":
    test_aura_explosion()
    print("Tests passed")
