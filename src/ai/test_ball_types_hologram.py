import pytest
from ai.action import Action
from ai.ball_types_hologram import Hologram

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.balls = []
        self.events = []
        self.arena = MockArena()

class MockEnemy:
    def __init__(self):
        self.id = 2
        self.team = "enemy_team"
        self.ball_type = "base"
        self.hp = 100
        self.is_blinded = False
        self.blindness_timer = 0.0

def test_hologram_spawn_clones():
    world = MockWorld()

    holo = Hologram(1, 100.0, 100.0)
    holo.ball_type = "hologram"
    holo.team = "holo_team"

    # Simulate movement
    holo.prev_x = 90.0
    holo.prev_y = 100.0
    holo.holo_clone_timer = 0.0

    world.balls.append(holo)

    action = Action(holo, world)
    action.execute("idle", 0.1)

    # Should have spawned a clone
    assert len(world.balls) == 2

    clone = world.balls[1]
    assert getattr(clone, "is_holo_clone", False) is True
    assert clone.hp == 1.0
    assert clone.damage == 0.0
    assert clone.holo_clone_lifetime == 2.0

def test_hologram_clone_collision_blind():
    world = MockWorld()

    clone = Hologram(3, 150.0, 150.0)
    clone.team = "holo_team"
    clone.is_holo_clone = True
    clone.hp = 1.0

    enemy = MockEnemy()

    action = Action(clone, world)
    action._attempt_damage(enemy, clone)

    assert clone.hp == 0
    assert clone.alive == False

    assert enemy.is_blinded is True
    assert enemy.blindness_timer == 2.0

    # Check if explosion event appended
    assert len(world.events) == 1
    assert world.events[0]['type'] == 'explosion'
