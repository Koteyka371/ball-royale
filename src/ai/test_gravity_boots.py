import sys
import os
sys.path.insert(0, os.path.abspath('src'))
from ai.action import Action
from ai.test_anchor_booster import MockBall, MockWorld, MockEntity

def test_gravity_boots_collection():
    ball = MockBall()
    booster = MockEntity(2, 0, 0, kind="gravity_boots")

    world = MockWorld()
    world.balls = [ball]
    world.entities = [ball]
    world.boosters = [booster]
    world.arena.hazards = [booster]

    action = Action(ball, world)
    action.execute("collect_booster", 1.0)

    assert hasattr(ball, "inventory")
    assert "gravity_boots" in ball.inventory
    assert len(world.arena.hazards) == 0
    assert len(world.boosters) == 0

def test_gravity_boots_pull_reduction():
    # Setup ball without boots
    ball1 = MockBall()
    ball1.x = 100
    ball1.y = 100

    # Setup ball with boots
    ball2 = MockBall()
    ball2.x = 100
    ball2.y = 100
    ball2.inventory = ["gravity_boots"]

    gw = type('MockHazard', (), {'id': 99, 'x': 100, 'y': 0, 'kind': 'gravity_well', 'radius': 500, 'damage': 0.0})()

    world1 = MockWorld()
    world1.balls = [ball1]
    world1.arena.hazards = [gw]

    world2 = MockWorld()
    world2.balls = [ball2]
    world2.arena.hazards = [gw]

    action1 = Action(ball1, world1)
    # Stub movement
    action1._idle = lambda d: None
    action1._chase = lambda d: None
    action1._attack = lambda d: None
    action1._process_physics = lambda delta: None
    action1.execute("idle", 0.1)

    action2 = Action(ball2, world2)
    # Stub movement
    action2._idle = lambda d: None
    action2._chase = lambda d: None
    action2._attack = lambda d: None
    action2._process_physics = lambda delta: None
    action2.execute("idle", 0.1)

    # ball1 should be pulled significantly more than ball2 towards (100, 0)
    # y decreases from 100 towards 0
    delta1 = 100 - ball1.y
    delta2 = 100 - ball2.y

    assert delta2 > 0
    assert delta1 > delta2
    assert delta2 < delta1 * 0.2  # Should be ~10% of delta1

if __name__ == "__main__":
    test_gravity_boots_collection()
    test_gravity_boots_pull_reduction()
    print("Tests passed")
