import pytest
from ai.test_action_advanced import MockWorld, MockBall
from ai.action import Action
from ai.ball_types_replicant import Replicant

def test_replicant_spawn_clones():
    owner = Replicant(111, 10, 10)
    owner.team = "owner_team"
    owner.vx = 50.0
    owner.vy = 20.0

    world = MockWorld()
    world.balls = [owner]
    action = Action(owner, world)

    owner.skill = "passive_replicant"
    owner.skill_timer = 0.0
    action._use_skill()

    assert len(world.balls) == 2

    clone = world.balls[1]
    assert getattr(clone, "is_replicant_clone", False) is True
    assert clone.hp == 1.0
    assert clone.damage == 0.0
    assert clone.vx == 50.0
    assert clone.vy == 20.0
    assert clone.mimic_owner == owner.id
    assert clone.skill is None
    assert owner.skill_timer > 0.0

def test_replicant_clone_collision_blind():
    owner = Replicant(111, 10, 10)
    owner.team = "owner_team"

    clone = MockBall(x=10, y=10)
    clone.is_replicant_clone = True
    clone.team = "owner_team"
    clone.hp = 1.0
    clone.alive = True

    enemy = MockBall(x=12, y=10)
    enemy.is_blinded = False
    enemy.blindness_timer = 0.0
    enemy.radius = 10.0
    clone.radius = 10.0
    enemy.team = "enemy_team"
    enemy.hp = 100.0
    enemy.alive = True

    world = MockWorld()
    world.balls = [clone, enemy]
    world.events = []
    world.get_nearby_entities = lambda b, r: world.balls

    action = Action(clone, world)
    action._resolve_collisions()

    assert enemy.is_blinded is True
    assert enemy.blindness_timer == 2.0
    assert clone.hp == 0
    assert clone.alive is False
    assert any(e["type"] == "explosion" and e["color"] == "magenta" for e in world.events)
