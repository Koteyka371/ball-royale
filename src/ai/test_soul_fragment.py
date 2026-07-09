import pytest
from ai.game_modes import BattleRoyaleMode
from ai.action import Action

class MockBall:
    def __init__(self, bid, ball_type):
        self.id = bid
        self.ball_type = ball_type
        self.x = 100.0
        self.y = 100.0
        self.radius = 20.0
        self.max_hp = 100.0
        self.hp = 100.0
        self.damage = 10.0
        self.base_damage = 10.0
        self.alive = True
        self.is_elite_minion = False
        self.minion_owner = None
        self.__class__.BALL_TYPE = ball_type

class Hazard:
    def __init__(self, id, x, y, radius, kind, damage):
        self.id = id
        self.x = x
        self.y = y
        self.radius = radius
        self.kind = kind
        self.damage = damage
        self.active = True
        self.is_disabled_by_flare = False
        self.minion_owner = None

class MockWorld:
    def __init__(self):
        self.balls = []
        self.events = []
        class Arena:
            def __init__(self):
                self.hazards = []
        self.arena = Arena()
        self.safe_zone_center = (500, 500)
        self.safe_zone_radius = 500

    def clamp_position(self, x, y, r):
        return x, y, False

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

def test_elite_minion_drops_soul_fragment():
    mode = BattleRoyaleMode()
    world = MockWorld()

    elite = MockBall(2, "elite_minion")
    elite.is_elite_minion = True
    elite.minion_owner = 1
    elite.hp = 0
    elite.alive = False

    necro = MockBall(1, "necromancer")
    world.balls = [necro, elite]

    # Trigger death logic
    mode.on_ball_died(world, elite, necro)

    assert len(world.arena.hazards) == 1
    soul = world.arena.hazards[0]
    assert getattr(soul, "kind", "") == "soul_fragment"
    assert getattr(soul, "minion_owner", None) == 1

def test_necromancer_collects_soul_fragment():
    world = MockWorld()
    necro = MockBall(1, "necromancer")
    world.balls = [necro]

    soul = Hazard("soul_1", 100.0, 100.0, 15.0, "soul_fragment", 0.0)
    soul.minion_owner = 1
    world.arena.hazards.append(soul)

    action = Action(necro, world)
    action.execute({}, delta=0.016)

    assert necro.max_hp == 102.0
    assert necro.hp == 102.0
    assert necro.damage == 11.0
    assert necro.base_damage == 11.0
    assert len(world.arena.hazards) == 0

def test_other_ball_cannot_collect_soul_fragment():
    world = MockWorld()
    other = MockBall(2, "warrior")
    world.balls = [other]

    soul = Hazard("soul_1", 100.0, 100.0, 15.0, "soul_fragment", 0.0)
    soul.minion_owner = 1
    world.arena.hazards.append(soul)

    action = Action(other, world)
    action.execute({}, delta=0.016)

    assert other.max_hp == 100.0
    assert len(world.arena.hazards) == 1

def test_wrong_necromancer_cannot_collect_soul_fragment():
    world = MockWorld()
    necro2 = MockBall(2, "necromancer") # Wrong owner ID
    world.balls = [necro2]

    soul = Hazard("soul_1", 100.0, 100.0, 15.0, "soul_fragment", 0.0)
    soul.minion_owner = 1
    world.arena.hazards.append(soul)

    action = Action(necro2, world)
    action.execute({}, delta=0.016)

    assert necro2.max_hp == 100.0
    assert len(world.arena.hazards) == 1
