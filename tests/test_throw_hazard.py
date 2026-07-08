import pytest
from ai.action import Action
from arena.procedural_arena import Hazard

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards

class MockWorld:
    def __init__(self, arena, balls):
        self.arena = arena
        self.balls = balls
        self.entities = balls

    def get_nearby_entities(self, entity, radius):
        return [b for b in self.balls if b != entity]

class MockBall:
    def __init__(self, id, x, y, skill, team=""):
        self.id = id
        self.x = x
        self.y = y
        self.skill = skill
        self.skill_timer = 0.0
        self.skill_cooldown = 4.0
        self.silence_timer = 0.0
        self.radius = 10.0
        self.alive = True
        self.ball_type = "brawler" if id == 1 else "enemy"
        self.team = team

def test_throw_hazard_skill():
    # Setup hazard near the brawler
    h1 = Hazard(1, 15, 0, 10, "lava_rock", 20.0)
    h2 = Hazard(2, 500, 500, 10, "lava_rock", 20.0)

    arena = MockArena([h1, h2])

    brawler = MockBall(1, 0, 0, "throw_hazard", team="teamA")
    enemy = MockBall(2, 100, 0, "none", team="teamB")

    world = MockWorld(arena, [brawler, enemy])
    action = Action(brawler, world)

    assert len(arena.hazards) == 2

    # Use skill
    action._use_skill()

    # h1 should be removed, a new hazard (thrown_rock) should be added
    assert h1 not in arena.hazards
    assert len(arena.hazards) == 2 # h2 + new thrown rock

    thrown_rock = arena.hazards[-1]
    assert thrown_rock.kind == "thrown_rock"
    assert thrown_rock.damage == 50.0
    assert thrown_rock.duration == 2.0
    assert thrown_rock.vx > 0 # Moving towards enemy at x=100
    assert thrown_rock.vy == 0
    assert brawler.skill_timer == 4.0
