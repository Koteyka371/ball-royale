import sys
import os
sys.path.insert(0, os.path.abspath('src'))
from ai.ghost_companion import GhostCompanionManager

class MockBall:
    def __init__(self, id, team, x, y, alive=True, hp=100.0, max_hp=100.0):
        self.id = id
        self.team = team
        self.x = x
        self.y = y
        self.alive = alive
        self.hp = hp
        self.max_hp = max_hp

class MockWorld:
    def __init__(self):
        self.balls = []

def test_ghost_companion_spawn_and_attach():
    world = MockWorld()
    manager = GhostCompanionManager()

    dead_ball = MockBall(1, "red", 100.0, 100.0, alive=False)
    alive_ally = MockBall(2, "red", 200.0, 100.0, hp=50.0)
    alive_enemy = MockBall(3, "blue", 100.0, 200.0, hp=100.0)

    world.balls = [dead_ball, alive_ally, alive_enemy]

    # Tick 1: Spawn ghost
    manager.update(1.0, world)
    assert len(manager.ghosts) == 1
    ghost = manager.ghosts[0]
    assert ghost.owner_id == 1
    assert ghost.team == "red"

    # Move ally close to ghost
    alive_ally.x = 110.0

    # Tick 2: Move ghost closer to ally
    manager.update(1.0, world)

    # Tick 3: Attach to ally
    alive_ally.x = ghost.x + 5.0
    manager.update(1.0, world)
    assert ghost.target_id == 2

    # Tick 4: Heal ally
    manager.update(1.0, world)
    assert alive_ally.hp == 55.0

    # Kill ally, ghost should detach
    alive_ally.alive = False

    # Tick 5: Detach and spawn new ghost for ally
    manager.update(1.0, world)
    assert ghost.target_id is None
    assert len(manager.ghosts) == 2

    # Move enemy close to first ghost
    alive_enemy.x = ghost.x + 5.0
    alive_enemy.y = ghost.y + 5.0

    # Tick 6: Attach to enemy
    manager.update(1.0, world)
    assert ghost.target_id == 3

    # Tick 7: Damage enemy
    manager.update(1.0, world)
    assert alive_enemy.hp == 95.0
