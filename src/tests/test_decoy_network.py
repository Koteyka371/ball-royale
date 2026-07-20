import pytest
from ai.game_modes import GAME_MODES, DecoyNetworkMode

class MockBall:
    def __init__(self, id, is_decoy=False, owner_id=None, team="neutral"):
        self.id = id
        self.x = 0.0
        self.y = 0.0
        self.alive = True
        self.hp = 100.0
        self.max_hp = 100.0
        self.is_decoy = is_decoy
        self.owner_id = owner_id
        self.team = team

        # essential attributes
        self.ball_type = "basic"
        self.max_stamina = 100.0
        self.stamina = 100.0
        self.base_speed = 100.0
        self.speed = 100.0
        self.base_damage = 10.0
        self.original_base_damage = 10.0
        self.traits = []
        self.weather_immunity_timer = 0.0
        self.in_mirror_dimension = False
        self.intangible = False
        self.vision_radius = 500.0
        self.invisible = False

class MockWorld:
    def __init__(self):
        self.balls = []

def test_decoy_network_damage_pulse():
    mode = GAME_MODES['decoy_network']
    world = MockWorld()

    # Decoys network
    d1 = MockBall(1, is_decoy=True, owner_id=99, team="A")
    d1.x, d1.y = 100, 100
    d2 = MockBall(2, is_decoy=True, owner_id=99, team="A")
    d2.x, d2.y = 500, 500

    # Enemies
    enemy1 = MockBall(3, team="B")
    enemy1.x, enemy1.y = 110, 110 # Close to d1

    enemy2 = MockBall(4, team="B")
    enemy2.x, enemy2.y = 490, 490 # Close to d2

    enemy3 = MockBall(5, team="B")
    enemy3.x, enemy3.y = 1000, 1000 # Far away

    # Ally
    ally = MockBall(6, team="A")
    ally.x, ally.y = 105, 105 # Close to d1 but same team

    world.balls = [d1, d2, enemy1, enemy2, enemy3, ally]
    mode.setup(world, world.balls)

    # Tick to register initial HP and state
    mode.tick(world, world.balls)

    # Apply damage to ONE decoy
    d1.hp -= 20.0 # 20 damage taken

    # Tick to distribute damage pulse
    mode.tick(world, world.balls)

    # Total damage taken = 20. Pulse damage = 10.
    # d1 pulses 10 damage to enemy1.
    # d2 pulses 10 damage to enemy2.
    assert enemy1.hp == 90.0, f"Enemy1 should take 10 damage, has {enemy1.hp}"
    assert enemy2.hp == 90.0, f"Enemy2 should take 10 damage, has {enemy2.hp}"
    assert enemy3.hp == 100.0, "Enemy3 is too far and should be unaffected"
    assert ally.hp == 100.0, "Ally should not be damaged"

def test_decoy_network_fatal_damage():
    mode = GAME_MODES['decoy_network']
    world = MockWorld()

    d1 = MockBall(1, is_decoy=True, owner_id=99, team="A")
    d1.x, d1.y = 100, 100

    enemy1 = MockBall(2, team="B")
    enemy1.x, enemy1.y = 110, 110

    world.balls = [d1, enemy1]
    mode.setup(world, world.balls)
    mode.tick(world, world.balls)

    # Fatal damage to decoy
    d1.hp = 0.0
    d1.alive = False

    mode.tick(world, world.balls)

    # Decoy died (took 100 damage). Pulse = 50.
    assert enemy1.hp == 50.0, f"Enemy1 should take 50 damage, has {enemy1.hp}"
