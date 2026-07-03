import pytest
from ai.action import Action
from arena.procedural_arena import ProceduralArena, Hazard

class MockBall:
    def __init__(self):
        self.x = 100
        self.y = 100
        self.radius = 10
        self.hp = 50
        self.max_hp = 100
        self.alive = True
        self.ball_type = "test"
        self.team = "A"

class MockWorld:
    def __init__(self):
        self.arena = ProceduralArena(num_rooms=1)
        self.arena.hazards.clear()
        self.arena.hazards.append(Hazard(id=1, x=100, y=100, radius=50, kind="healing_spring", damage=-20))
        self.balls = []
        self.tick = 1
        self.width = 2000
        self.height = 2000

    def get_nearby_entities(self, ball, radius):
        return {"enemies": [], "allies": [], "boosters": []}

def test_healing_spring_regenerates_hp():
    ball = MockBall()
    world = MockWorld()
    world.balls.append(ball)
    action = Action(ball, world)

    initial_hp = ball.hp

    # Run the execute logic to apply healing
    action.execute("idle", 1.0)

    # Healing spring damage is -20, so it should heal 20 per second
    assert ball.hp > initial_hp
    assert ball.hp >= initial_hp + 20.0

def test_healing_spring_max_hp_cap():
    ball = MockBall()
    ball.hp = 90
    world = MockWorld()
    world.balls.append(ball)
    action = Action(ball, world)

    # Apply healing that exceeds max hp
    action.execute("idle", 1.0)

    # Should be capped at max_hp (100)
    assert ball.hp == 100
