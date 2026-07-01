import pytest
from ai.game_modes import CustomMatchMode

class MockWorld:
    def __init__(self):
        self.events = []
    def add_event(self, type, data):
        self.events.append((type, data))

class MockBall:
    def __init__(self, id, ball_type):
        self.id = id
        self.ball_type = ball_type
        self.alive = True
        self.team = ball_type
        self.radius = 15.0
        self.max_hp = 100.0
        self.hp = 100.0
        self.damage = 10.0
        self.base_damage = 10.0

def test_boss_mutator():
    mode = CustomMatchMode()
    mode.mutators = ["boss"]
    world = MockWorld()
    world.profile_manager = type('MockProfileManager', (), {'are_mutators_unlocked': lambda self: True})()

    balls = [
        MockBall(id=1, ball_type="tank"),
        MockBall(id=2, ball_type="sniper"),
        MockBall(id=3, ball_type="healer")
    ]

    mode.setup(world, balls)
    assert mode.mutators_active == True

    # Tick past 10 seconds to trigger boss
    mode.tick(world, balls, delta=10.1)

    # Verify one ball is boss
    bosses = [b for b in balls if getattr(b, "_is_boss_mutator", False)]
    assert len(bosses) == 1
    boss = bosses[0]

    assert boss.team == "Boss_Mutator"

    # Tick past 15 seconds to end boss mutator
    mode.tick(world, balls, delta=15.1)

    # Verify reverted
    assert not getattr(boss, "_is_boss_mutator", False)
    assert boss.team == boss._original_team

def test_boss_mutator_early_death():
    mode = CustomMatchMode()
    mode.mutators = ["boss"]
    world = MockWorld()
    world.profile_manager = type('MockProfileManager', (), {'are_mutators_unlocked': lambda self: True})()

    balls = [
        MockBall(id=1, ball_type="tank"),
        MockBall(id=2, ball_type="sniper"),
        MockBall(id=3, ball_type="healer")
    ]

    mode.setup(world, balls)

    # Tick past 10 seconds to trigger boss
    mode.tick(world, balls, delta=10.1)

    bosses = [b for b in balls if getattr(b, "_is_boss_mutator", False)]
    boss = bosses[0]

    # Kill the boss early
    boss.hp = 0
    boss.alive = False

    # Tick to process death and revert
    mode.tick(world, balls, delta=0.1)

    # Verify everyone reverts
    assert not getattr(boss, "_is_boss_mutator", False)
    assert boss.team == boss._original_team
    hunters = [b for b in balls if b != boss]
    for h in hunters:
        assert h.team == h._original_team

    # Verify timer resets and ticks again
    assert getattr(mode, "boss_mutator_timer", 0) > 0
    mode.tick(world, balls, delta=10.0)
    new_bosses = [b for b in balls if getattr(b, "_is_boss_mutator", False)]
    assert len(new_bosses) == 1
