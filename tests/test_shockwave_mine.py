import pytest
from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.events = []
        self.next_id = 100

class MockBall:
    def __init__(self, bid, team, x, y):
        self.id = bid
        self.team = team
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.alive = True
        self.hp = 100
        self.anchor_trap_timer = 0.0

def test_deploy_shockwave_mine():
    world = MockWorld()
    ball = MockBall(1, "red", 10.0, 20.0)
    world.balls.append(ball)

    ai = Action(ball, world)
    ball.skill = "deploy_shockwave_mine"
    ball.skill_timer = 0.0

    ai._use_skill()

    assert len(world.arena.hazards) == 1
    mine = world.arena.hazards[0]
    assert mine.kind == "shockwave_mine"
    assert mine.owner_id == 1
    assert mine.team == "red"
    assert mine.radius == 20.0

def test_shockwave_mine_detonates_on_enemy():
    world = MockWorld()
    ball = MockBall(1, "red", 10.0, 20.0) # Active ball running logic

    owner = MockBall(2, "blue", 100.0, 100.0)
    enemy1 = ball
    enemy2 = MockBall(3, "red", 300.0, 20.0) # Should be hit by shockwave (distance ~290)
    enemy3 = MockBall(4, "red", 1000.0, 1000.0) # Too far (distance > 400)
    ally = MockBall(5, "blue", 50.0, 20.0) # Should not be hit (same team as owner)

    world.balls.extend([owner, enemy1, enemy2, enemy3, ally])

    class MockHazard:
        pass

    mine = MockHazard()
    mine.kind = "shockwave_mine"
    mine.x = 10.0
    mine.y = 20.0
    mine.radius = 20.0
    mine.duration = 60.0
    mine.owner_id = 2
    mine.team = "blue"

    world.arena.hazards.append(mine)

    ai = Action(ball, world)
    ai.execute("survival", 1.0)

    # Mine should be removed
    assert mine not in world.arena.hazards

    # Event emitted
    assert len(world.events) == 1
    assert world.events[0]['type'] == 'explosion'

    # Enemy 1 (trigger) hit
    assert enemy1.hp == 90
    assert enemy1.vx != 0 or enemy1.vy != 0
    assert enemy1.anchor_trap_timer >= 1.5

    # Enemy 2 hit
    assert enemy2.hp == 90
    assert enemy2.vx != 0 or enemy2.vy != 0
    assert enemy2.anchor_trap_timer >= 1.5

    # Enemy 3 not hit
    assert enemy3.hp == 100
    assert enemy3.vx == 0
    assert enemy3.anchor_trap_timer == 0.0

    # Ally not hit
    assert ally.hp == 100
    assert ally.vx == 0
    assert ally.anchor_trap_timer == 0.0
