import sys
import os
import math

sys.path.insert(0, os.path.abspath('src'))
from ai.action import Action

class MockEntity:
    def __init__(self, id, x, y, kind=None):
        self.id = id
        self.x = x
        self.y = y
        self.kind = kind
        self.ball_type = "booster"
        self.duration = 5.0
        self.radius = 15.0
        self.damage = 0.0
        self.owner_id = None
        self.owner_team = ""

    def get(self, key, default=None):
        return getattr(self, key, default)

class MockBall:
    def __init__(self, id, team="team1"):
        self.id = id
        self.team = team
        self.x = 0
        self.y = 0
        self.radius = 10
        self.speed = 2
        self.base_speed = 10
        self.hp = 100
        self.max_hp = 100
        self.stamina = 100
        self.alive = True
        self.ball_type = "basic"
        self.perception_radius = 250.0
        self.inventory = []

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000
        self.height = 1000

    def update_zone(self, tick, delta=None):
        pass

    def clamp_position(self, x, y, radius=0):
        return x, y, False

class MockWorld:
    def __init__(self):
        self.balls = []
        self.boosters = []
        self.arena = MockArena()

    def get_nearby_entities(self, ball, radius):
        return {
            "enemies": [b for b in self.balls if b.team != ball.team],
            "allies": [],
            "boosters": [b for b in self.boosters if hasattr(b, 'kind') and 'booster' in b.kind]
        }

def test_disruptor_grenade_collect_and_deploy():
    brawler = MockBall(1, team="red")
    enemy = MockBall(2, team="blue")
    enemy.x = 100
    enemy.y = 0

    world = MockWorld()
    world.balls = [brawler, enemy]

    booster = MockEntity(3, 0, 0, kind="disruptor_grenade_booster")
    world.boosters = [booster]
    world.arena.hazards = [booster]

    action = Action(brawler, world)

    # 1. Collect booster
    action.execute("collect_booster", 1.0)

    # Booster should be removed from world
    assert len(world.boosters) == 0
    assert len(world.arena.hazards) == 0

    # Brawler should have disruptor_grenade in inventory
    assert "disruptor_grenade" in brawler.inventory

    # 2. Deploy grenade
    action.execute("attack", 1.0)

    # Grenade should be removed from inventory
    assert "disruptor_grenade" not in brawler.inventory

    # Grenade should be deployed in the world
    assert len(world.arena.hazards) == 1
    grenade = world.arena.hazards[0]
    assert getattr(grenade, 'kind', '') == "thrown_disruptor_grenade"
    assert getattr(grenade, 'owner_team', '') == "red"

    # 3. Fast forward time so grenade explodes
    grenade.duration = 0.05
    action.execute("attack", 0.1)

    # Grenade should be gone and blast should be there
    assert len(world.arena.hazards) == 1
    blast = world.arena.hazards[0]
    assert getattr(blast, 'kind', '') == "disruptor_blast"
    assert getattr(blast, 'owner_team', '') == "red"

    # 4. Enemy caught in blast gets disruption timer
    action_enemy = Action(enemy, world)
    action_enemy.execute("attack", 0.1)

    assert getattr(enemy, "aura_disruption_timer", 0.0) == 9.9

if __name__ == "__main__":
    test_disruptor_grenade_collect_and_deploy()
    print("Disruptor grenade test passed!")
