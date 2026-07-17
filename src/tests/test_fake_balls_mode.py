from ai.game_modes import GameMode, GAME_MODES, FakeBall

def test_fake_balls_mode():
    mode = GAME_MODES['fake_balls']
    class MockArena:
        width = 1000
        height = 1000
    class MockWorld:
        def __init__(self):
            self.arena = MockArena()
            self.balls = []
            self.next_id = 1000

    world = MockWorld()

    # Tick below interval doesn't spawn
    mode.tick(world, world.balls, 9.0)
    assert len(world.balls) == 0

    # Tick crossing interval spawns a fake ball
    mode.tick(world, world.balls, 2.0)
    assert len(world.balls) == 1
    assert isinstance(world.balls[0], FakeBall)
    assert world.balls[0].hp == 1.0

    fake = world.balls[0]
    initial_x, initial_y = fake.x, fake.y

    # Force timer below 0 to generate a target, and move towards it
    fake.move_timer = 0
    fake.update(1.0, 1000, 1000)

    # Expect position to change
    assert fake.x != initial_x or fake.y != initial_y

    # Deal damage
    fake.take_damage(10)
    assert fake.hp <= 0
    assert not fake.alive

    # Next tick should clean up the dead ball
    mode.tick(world, world.balls, 0.1)
    assert len(world.balls) == 0
