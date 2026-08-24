import pytest
from ai.game_modes import GameMode

class MockArena:
    def __init__(self):
        self.is_raining = True

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

    def add_event(self, event, payload):
        pass

class MockBall:
    def __init__(self, id, ball_type):
        self.id = id
        self.ball_type = ball_type
        self.traits = []
        self.alive = True
        self.speed = 100.0
        self.team = "team1"
        self.x, self.y = 0, 0
        self.hp = 100.0
        self.stamina = 100.0

def test_thunderstorm_aura_raining():
    world = MockWorld()

    b1 = MockBall(1, "water_elemental")
    b1.team = "team1"
    b1.x, b1.y = 0, 0

    b2 = MockBall(2, "lightning_elemental")
    b2.team = "team1"
    b2.x, b2.y = 100, 100

    b3 = MockBall(3, "lightning_elemental")
    b3.team = "team1"
    b3.x, b3.y = 500, 500 # Ensure b2 doesn't trigger the test accidentally

    enemy = MockBall(4, "normal")
    enemy.team = "team2"
    enemy.x, enemy.y = 220, 0 # within 250 (amplified), outside 200 (old amplified)

    mode = GameMode()
    balls = [b1, b3, enemy] # Note: b1 is at 0,0, enemy at 220,0. Dist=220.

    # Fast forward to 1.0 second for the shock aura pulse
    for i in range(101):
        mode.apply_dynamic_traits(world, balls, 0.01)

    assert enemy.hp < 100.0, f"Enemy HP remained {enemy.hp}"
    assert b1.stamina < 100.0, f"b1 stamina remained {b1.stamina}"

def test_thunderstorm_aura_not_raining():
    world = MockWorld()
    world.arena.is_raining = False

    b1 = MockBall(1, "water_elemental")
    b1.team = "team1"
    b1.x, b1.y = 0, 0

    b2 = MockBall(2, "lightning_elemental")
    b2.team = "team1"
    b2.x, b2.y = 100, 100

    b3 = MockBall(3, "lightning_elemental")
    b3.team = "team1"
    b3.x, b3.y = 500, 500 # Note b2 is 100,100, and enemy is 180,0 -> dist is sqrt(80^2 + 100^2) = sqrt(6400+10000) = sqrt(16400) = 128. This is < 150!! b2 is shocking the enemy!!
    # Let's fix that.

    enemy = MockBall(4, "normal")
    enemy.team = "team2"
    enemy.x, enemy.y = 180, 0 # within 250 (amplified), outside 150 (normal)

    mode = GameMode()
    balls = [b1, b3, enemy]

    # Fast forward to 1.0 second for the shock aura pulse
    for i in range(101):
        mode.apply_dynamic_traits(world, balls, 0.01)

    print("dist_sq to enemy:", (b1.x - enemy.x)**2 + (b1.y - enemy.y)**2)

    assert enemy.hp == 100.0, f"Enemy HP changed to {enemy.hp}"
    assert b1.stamina == 100.0, f"b1 stamina changed to {b1.stamina}"

if __name__ == '__main__':
    test_thunderstorm_aura_not_raining()
