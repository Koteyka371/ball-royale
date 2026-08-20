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
    arena = MockArena([]); arena.width = 1000; arena.height = 1000; arena.width = 1000; arena.height = 1000
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

    # Move enemy slightly away from bomb to test impact
    enemy.x = bomb.x + 10
    enemy.y = bomb.y

    # Execute a frame to trigger impact
    action.execute("idle", 0.016)

    # Bomb should detonate on impact
    assert bomb.duration == 0.0

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

def test_bomb_bounce():
    arena = MockArena([]); arena.width = 1000; arena.height = 1000; arena.width = 1000; arena.height = 1000
    brawler = MockBall(1, 10, 10, "throw_bomb", team="teamA")
    world = MockWorld(arena, [brawler])
    action = Action(brawler, world)

    # Manually spawn bomb near wall
    bomb = type("Hazard", (), {})()
    bomb.kind = "thrown_bomb"
    bomb.x = 5
    bomb.y = 500
    bomb.vx = -400
    bomb.vy = 0
    bomb.duration = 2.0
    bomb.owner_id = 1
    bomb.radius = 15
    arena.hazards.append(bomb)

    action.execute("idle", 0.1)

    # Should have bounced
    assert bomb.x >= 15
    assert bomb.vx > 0
