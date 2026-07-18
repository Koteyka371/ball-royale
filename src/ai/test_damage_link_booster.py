import pytest
from unittest.mock import MagicMock
from ai.action import Action

class FakeBall:
    def __init__(self, x=0.0, y=0.0, hp=100.0, alive=True):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = 100.0
        self.alive = alive
        self.id = id(self)
        self.team = "solo"
        self.ball_type = "basic"
        self.radius = 10.0
        self._prev_hp = hp

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False

class FakeHazard:
    def __init__(self, kind, x=0.0, y=0.0):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = 10.0
        self.damage = 0.0
        self.active = True

def test_damage_link_booster_collection():
    ball = FakeBall(0.0, 0.0)
    enemy = FakeBall(50.0, 0.0)
    enemy.team = "enemy"
    enemy.ball_type = "basic2"
    enemy.ball_type = "basic2"

    world = MagicMock()
    world.flare_light_timer = 0.0
    world.balls = [ball, enemy]
    world.arena.safe_zone_center = (500, 500)
    world.arena.safe_zone_radius = 2000
    world.arena.is_in_safe_zone.return_value = True
    world.arena.clamp_position.return_value = (0, 0, False)
    world.arena.danger_grid = {}

    booster = FakeHazard("damage_link_booster", 5.0, 0.0)
    world.arena.hazards = [booster]
    world.boosters = [booster]

    action = Action(ball, world)
    action.execute("collect_booster", 1.0)

    assert getattr(ball, "damage_link_target", None) == enemy
    assert getattr(enemy, "damage_link_target", None) == ball

def test_damage_link_booster_damage_sharing():
    ball = FakeBall(0.0, 0.0)
    enemy = FakeBall(50.0, 0.0)
    enemy.team = "enemy"
    enemy.ball_type = "basic2"
    enemy.ball_type = "basic2"

    ball.damage_link_target = enemy
    enemy.damage_link_target = ball

    world = MagicMock()
    world.flare_light_timer = 0.0
    world.balls = [ball, enemy]
    world.arena.hazards = []
    world.arena.safe_zone_center = (500, 500)
    world.arena.safe_zone_radius = 2000
    world.arena.is_in_safe_zone.return_value = True
    world.arena.clamp_position.return_value = (0, 0, False)
    world.arena.danger_grid = {}

    action = Action(ball, world)

    # Simulate ball taking 20 damage before action execution
    # Actually wait, the damage taken calculation in execute uses `start_hp = current_hp` at top of execute,
    # so we need to test how it shares damage.
    # The damage link logic is triggered by hazard damage or other things in execute?
    # No, action.py execute calculates `damage_taken = start_hp - current_hp` at the BOTTOM of the method,
    # which means we need the damage to happen inside `execute()`.
    # Let's apply a hazard to damage `ball`

    hazard = FakeHazard("fire", 0.0, 0.0)
    hazard.damage = 20.0
    world.arena.hazards = [hazard]

    action.execute("idle", 1.0)

    # ball takes 20 damage (now 80 hp)
    assert ball.hp == 80.0
    # enemy should take 10 damage (half of 20) (now 90 hp)
    assert enemy.hp == 90.0

    # Ensure no recursion happens
    action_enemy = Action(enemy, world)
    world.arena.hazards = []
    enemy.hp = 70.0 # simulate another 20 damage happening elsewhere
    action_enemy.execute("flee", 1.0)

    # Since damage_taken logic checks `start_hp - current_hp`, changing hp directly and calling execute
    # will see `start_hp` as 70, not triggering damage. Let's add hazard.

    hazard2 = FakeHazard("fire", 50.0, 0.0)
    hazard2.damage = 20.0
    world.arena.hazards = [hazard2]

    action_enemy.execute("idle", 1.0)
    assert enemy.hp == 50.0
    assert ball.hp == 70.0
