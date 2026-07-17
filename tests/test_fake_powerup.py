import math
from ai.action import Action

class MockBall:
    def __init__(self, id, x, y, team):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.ball_type = team
        self.hp = 100.0
        self.vx = 0.0
        self.vy = 0.0
        self.stun_timer = 0.0
        self.alive = True
    def take_damage(self, dmg):
        self.hp -= dmg

class MockHazard:
    pass

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.balls = []
        self.arena = MockArena()
        self.boosters = []
    def get_nearby_entities(self, ball, radius):
        return {"enemies": [], "allies": []}

def test_fake_powerup_skill():
    world = MockWorld()
    owner = MockBall("1", -100, 0, "teamA")
    owner.skill = "place_fake_powerup"
    owner.skill_timer = 0.0
    world.balls.append(owner)

    action = Action(owner, world)
    action._spawn_skill_particles = lambda x: None
    action._use_skill()

    assert len(world.arena.hazards) == 1
    hazard = world.arena.hazards[0]
    assert hazard.kind == "fake_powerup"
    assert hazard.damage == 100.0
    assert hazard.owner_id == "1"

def test_fake_powerup_collection_enemy():
    world = MockWorld()
    owner = MockBall("1", -100, 0, "teamA")
    enemy = MockBall("2", 10, 0, "teamB")
    world.balls.extend([owner, enemy])

    hazard = MockHazard()
    hazard.kind = "fake_powerup"
    hazard.x = 10
    hazard.y = 0
    hazard.radius = 15.0
    hazard.damage = 100.0
    hazard.stun_duration = 2.0
    hazard.owner_id = "1"
    hazard.active = True
    world.arena.hazards.append(hazard)

    action = Action(enemy, world)
    action._idle = lambda x: None
    action._get_enemies_internal = lambda: [owner]
    # simulate collection by having enemy near hazard
    action._get_boosters = lambda: [hazard]
    action._get_boosters = lambda: [hazard]
    action._collect_booster(1.0)

    # The enemy should take 100 damage (hp drops from 100 to 0)
    assert enemy.hp == 0.0
    # The hazard should be removed
    assert hazard not in world.arena.hazards

def test_fake_powerup_collection_ally():
    world = MockWorld()
    owner = MockBall("1", -100, 0, "teamA")
    ally = MockBall("3", 10, 0, "teamA")
    world.balls.extend([owner, ally])

    hazard = MockHazard()
    hazard.kind = "fake_powerup"
    hazard.x = 10
    hazard.y = 0
    hazard.radius = 15.0
    hazard.damage = 100.0
    hazard.stun_duration = 2.0
    hazard.owner_id = "1"
    hazard.active = True
    world.arena.hazards.append(hazard)

    action = Action(ally, world)
    action._idle = lambda x: None
    action._get_enemies_internal = lambda: []
    # simulate collection by having ally near hazard
    action._get_boosters = lambda: [hazard]
    action._get_boosters = lambda: [hazard]
    action._collect_booster(1.0)

    # The ally should take NO damage
    assert ally.hp == 100.0
    # The hazard should be removed quietly
    assert hazard not in world.arena.hazards
