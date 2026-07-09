import pytest
from ai.action import Action

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards

class MockWorld:
    def __init__(self, arena, balls):
        self.arena = arena
        self.balls = balls
        self.entities = balls

    def get_nearby_entities(self, entity, radius):
        return {"enemies": [b for b in self.balls if b != entity]}

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
        self.hp = 100.0
        self.vx = 0.0
        self.vy = 0.0

def test_throw_bomb_skill():
    arena = MockArena([])
    brawler = MockBall(1, 0, 0, "throw_bomb", team="teamA")
    enemy = MockBall(2, 100, 0, "none", team="teamB")

    world = MockWorld(arena, [brawler, enemy])
    action = Action(brawler, world)

    action._use_skill()

    # Needs to spawn a thrown_bomb hazard moving to enemy
    assert len(arena.hazards) == 1
    bomb = arena.hazards[0]
    assert bomb.kind == "thrown_bomb"
    assert getattr(bomb, "duration", 0) > 0

    # Move enemy slightly away from bomb to test suction
    enemy.x = bomb.x + 50
    enemy.y = bomb.y
    old_x = enemy.x

    # Execute a frame to trigger suction
    action.execute("idle", 0.016)

    # Enemy should be sucked towards bomb
    assert enemy.x < old_x

    # Advance time to explode
    bomb.duration = 0.001
    action.execute("idle", 0.016)

    # Bomb should be removed and explosion spawned
    assert bomb not in arena.hazards
    assert len(arena.hazards) == 1
    exp = arena.hazards[0]
    assert exp.kind == "explosion"
    assert exp.radius == 150.0
    assert exp.damage == 150.0
