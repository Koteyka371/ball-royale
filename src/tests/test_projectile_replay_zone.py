import pytest
from ai.game_modes import ProjectileReplayZoneMode

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.projectiles = []

class MockProjectile:
    def __init__(self, x, y, vx, vy, team):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.team = team
        self.damage = 10
        self.shooter_id = 1
        self.is_projectile = True

def test_projectile_replay_zone():
    mode = ProjectileReplayZoneMode()
    world = MockWorld()

    # Tick to initialize
    mode.tick(world, [], 0.016)

    assert len(world.arena.hazards) == 1
    hazard = world.arena.hazards[0]
    assert hazard.kind == 'projectile_replay_zone'
    assert len(hazard.recorded_projectiles) == 0

    # Add a projectile inside the zone
    proj1 = MockProjectile(10, 10, 100, 0, 1)
    world.projectiles.append(proj1)

    mode.tick(world, [], 0.016)

    # Should be recorded
    assert len(hazard.recorded_projectiles) == 1
    assert hazard.recorded_projectiles[0]['vx'] == 100
    assert hazard.recorded_projectiles[0]['time_left'] > 0
    assert getattr(proj1, 'recorded_in_zone', False) == True

    # Tick past the replay interval (2.0)
    mode.tick(world, [], 2.0)

    # Should have replayed the projectile
    assert len(world.projectiles) == 2
    new_proj = world.projectiles[1]
    assert new_proj.vx == 100
    assert getattr(new_proj, 'recorded_in_zone', False) == True

    # Tick past record duration (15.0)
    mode.tick(world, [], 15.0)
    assert len(hazard.recorded_projectiles) == 0
