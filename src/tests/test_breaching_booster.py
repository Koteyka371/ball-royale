import pytest
from ai.action import Action
from arena.arena_types import ProceduralArena
from arena.procedural_arena import Room, Corridor

def test_breaching_booster():
    # Setup world with a wall between (100, 100) and (200, 100)
    class DummyBall:
        def __init__(self):
            self.id = 1
            self.x = 100
            self.y = 100
            self.vx = 500
            self.vy = 0
            self.radius = 10
            self.alive = True
            self.breaching_booster_timer = 5.0
            self.intangible = False
            self.intangible_timer = 0.0
            self.phase_booster_timer = 0.0

    class DummyWorld:
        def __init__(self):
            self.balls = []
            self.events = []
            self.arena = ProceduralArena(1000, num_rooms=1)
            # Create a small room at 50,50 100x100.
            self.arena.rooms.clear()
            self.arena.rooms.append(Room(0, 0, 100, 200))
            # x=100 is a wall.

        def add_event(self, type, data):
            self.events.append({'type': type, 'data': data})

    world = DummyWorld()
    ball = DummyBall()
    world.balls.append(ball)

    action = Action(ball, world)

    # Try to move through the wall
    ball.x += ball.vx * 0.1
    action._clamp_position()

    # Normally clamp_position would bounce it back inside 0,0 - 100,200
    # But with breaching_booster, it should be able to move and create a new room.
    assert ball.x == 150.0
    assert len(world.arena.rooms) == 2

    # Timer decrement test
    action.execute("idle", 0.016)
    assert ball.breaching_booster_timer < 5.0
