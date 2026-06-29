import sys
import os

# Add src to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.action import Action
from arena.procedural_arena import ProceduralArena, Hazard

class MockBall:
    def __init__(self, x=0, y=0, ball_type="warrior", id=1):
        self.x = x
        self.y = y
        self.ball_type = ball_type
        self.id = id
        self.team = "A"
        self.perception_radius = 500
        self.alive = True

class MockWorld:
    def __init__(self):
        self.arena = ProceduralArena(1000)
        self.balls = []

    def get_nearby_entities(self, ball, radius):
        return [b for b in self.balls if b != ball and b.alive]

def test_flare_targeting():
    world = MockWorld()

    # Add a flare
    flare = Hazard(id=0, x=50, y=50, radius=20, kind="flare", damage=0.0)
    world.arena.hazards = [flare]

    b1 = MockBall(0, 0, "warrior", 1)
    b2 = MockBall(100, 100, "warrior", 2)
    b2.team = "B"
    b2.ball_type = "scout"

    world.balls = [b1, b2]

    action = Action(b1, world)

    enemies = action._get_enemies()

    # Both flare and enemy ball should be in enemies list
    assert len(enemies) == 2
    assert flare in enemies
    assert b2 in enemies

    target = action._get_target(enemies)

    # Flare is closer and should be the priority target due to flare logic
    assert target == flare
