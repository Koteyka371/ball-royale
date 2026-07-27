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
        self.events = []
        self.tick = 0

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

def test_throw_boomerang_skill():
    arena = MockArena([])
    player = MockBall(1, 0, 0, "throw_boomerang", team="teamA")
    enemy = MockBall(2, 50, 0, "none", team="teamB")

    world = MockWorld(arena, [player, enemy])
    action = Action(player, world)

    action._use_skill()

    # Needs to spawn a thrown_boomerang hazard moving to enemy
    assert len(arena.hazards) == 1
    boomerang = arena.hazards[0]
    assert boomerang.kind == "thrown_boomerang"
    assert getattr(boomerang, "state", "") == "outgoing"
    assert boomerang.vx > 0
    assert boomerang.vy == 0

    # Tick execution (move boomerang outwards)
    action.execute("idle", 0.05)

    # Check if it hit the enemy
    assert enemy.hp < 100.0
    initial_hp = enemy.hp

    # Advance time to pause state
    boomerang.duration = 0.001
    action.execute("idle", 0.05)

    assert boomerang.state == "paused"

    # Advance time to returning state
    boomerang.pause_timer = 0.001
    action.execute("idle", 0.05)

    assert boomerang.state == "returning"

    # It should hit the enemy again as it returns
    # Let's place the enemy in its path
    enemy.x = boomerang.x - 5
    enemy.y = boomerang.y
    action.execute("idle", 0.05)

    assert enemy.hp < initial_hp

    # Let's place the player exactly where the boomerang is to make it disappear
    player.x = boomerang.x
    player.y = boomerang.y
    action.execute("idle", 0.05)

    assert boomerang not in arena.hazards or getattr(boomerang, 'active', True) == False
