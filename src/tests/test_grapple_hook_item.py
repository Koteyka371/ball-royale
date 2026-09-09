class MockWorld:
    def __init__(self):
        self.events = []
        self.balls = []
        self.arena = type('Arena', (), {'width': 1000, 'height': 1000, 'hazards': []})()

class MockBall:
    def __init__(self, x, y, id="1"):
        self.x = x
        self.y = y
        self.id = id
        self.vx = 0.0
        self.vy = 0.0
        self.hp = 100.0
        self.radius = 15.0
        self.alive = True
        self.inventory = []
        self.use_item = False
        self.speed = 100.0

    def __getattr__(self, name):
        if name in ('fx', 'fy'): return 0.0
        return super().__getattribute__(name)

def test_grapple_hook_item_collection():
    from ai.action import Action
    ball = MockBall(500, 500)
    world = MockWorld()
    item = type('Item', (), {'kind': 'grapple_hook_item', 'x': 500, 'y': 500, 'radius': 15.0, 'active': True})()
    world.boosters = [item]

    action = Action(ball, world)
    action._get_boosters = lambda: [item]
    action._collect_booster(0.1)

def test_grapple_hook_item_use_enemy():
    from ai.action import Action
    ball = MockBall(500, 500)
    ball.inventory = ["grapple_hook_item"]
    ball.use_item = True

    enemy = MockBall(500, 100, id="2")
    world = MockWorld()
    world.balls = [ball, enemy]

    action = Action(ball, world)
    # the execute tick will modify velocities significantly based on target, state etc.
    # so we just check that it properly handles the item logic without crashing
    # and sets the states correctly.
    action.execute("idle", 0.1) # idle does not trigger item use.
    # Use attack which triggers item
    action.execute("attack", 0.1)

    assert "grapple_hook_item" not in ball.inventory
    assert ball.use_item == False

    assert enemy.hp < 100.0

def test_grapple_hook_item_use_wall():
    from ai.action import Action
    ball = MockBall(100, 500)
    ball.inventory = ["grapple_hook_item"]
    ball.use_item = True

    world = MockWorld()
    world.balls = [ball]

    action = Action(ball, world)
    action.execute("attack", 0.1)

    assert "grapple_hook_item" not in ball.inventory
    assert ball.use_item == False
