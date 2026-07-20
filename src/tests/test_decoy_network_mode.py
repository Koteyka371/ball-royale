import pytest
from ai.game_modes import GAME_MODES, DecoyNetworkMode

class MockBall:
    def __init__(self, x=0, y=0, team="red", id=1):
        self.id = id
        self.x = x
        self.y = y
        self.hp = 100.0
        self.max_hp = 100.0
        self.team = team
        self.alive = True
        self.is_decoy = False
        self.is_hologram_decoy = False
        self.ball_type = "basic"
        self.max_stamina = 100.0
        self.stamina = 100.0
        self.base_speed = 5.0
        self.speed = 5.0
        self.base_damage = 10.0
        self.original_base_damage = 10.0
        self.traits = []
        self.weather_immunity_timer = 0.0
        self.in_mirror_dimension = False
        self.intangible = False
        self.vision_radius = 200.0
        self.invisible = False

class MockWorld:
    def __init__(self):
        self.balls = []
        self.next_id = 1000

def test_decoy_network_spawn():
    mode = GAME_MODES["decoy_network"]
    world = MockWorld()
    b1 = MockBall(x=10, y=10, team="red", id=1)
    b2 = MockBall(x=50, y=50, team="blue", id=2)
    world.balls = [b1, b2]

    mode.setup(world, world.balls)
    mode.tick(world, world.balls, 8.5) # spawn_interval is 8.0

    # Each player should have spawned a HologramDecoy
    holograms = [b for b in world.balls if getattr(b, "is_hologram_decoy", False)]
    assert len(holograms) == 2
    assert holograms[0].owner_id in [1, 2]
    assert holograms[1].owner_id in [1, 2]
    assert holograms[0].owner_id != holograms[1].owner_id

def test_decoy_network_ripple_damage():
    mode = GAME_MODES["decoy_network"]
    world = MockWorld()

    b1 = MockBall(x=10, y=10, team="red", id=1)
    b2 = MockBall(x=50, y=50, team="blue", id=2)

    world.balls = [b1, b2]
    mode.setup(world, world.balls)

    # Create two holograms manually for b1
    h1 = mode.HologramDecoy(b1)
    h1.x, h1.y = 100, 100 # Damaged far away
    h2 = mode.HologramDecoy(b1)
    h2.x, h2.y = 45, 45   # Close to b2 (enemy)

    world.balls.extend([h1, h2])

    # Damage h1
    h1.hp = 80.0 # Took 20 damage
    assert getattr(h1, "_prev_hp", 100.0) == 100.0

    # Tick to process damage and ripple
    mode.tick(world, world.balls, 0.016)

    # The damage should ripple from h2 to b2 (b2 is nearest enemy to h2)
    # The damage amount is 20
    assert b2.hp == 60.0

    # Tick again, b2 should not take more damage because prev_hp is updated
    mode.tick(world, world.balls, 0.016)
    assert b2.hp == 60.0
