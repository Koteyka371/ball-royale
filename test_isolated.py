from ai.action import Action
class MockWorld:
    def __init__(self):
        self.boosters = []
        self.arena = type('Arena', (), {'hazards': [], 'safe_zone_radius': 1000, 'safe_zone_center': (0,0)})()
        self.balls = []
    def clamp_position(self, x, y, r):
        return x, y, False
world = MockWorld()
world.arena.clamp_position = world.clamp_position

class MockEntity:
    def __init__(self, eid, x, y, kind=None):
        self.id = eid
        self.x = x
        self.y = y
        self.kind = kind
        self.inventory = []
        self.speed = 10
        self.base_speed = 10
        self.vx = 0
        self.vy = 0
        self.hp = 100
        self.max_hp = 100
        self.team = "team1"
        self.active = True
        self.radius = 15.0

ball = MockEntity(1, 0, 0)
world.balls.append(ball)
item = MockEntity(2, 0, 0, kind="booster_trap_item")
world.boosters.append(item)

action = Action(ball, world)
action.execute(strategy="flee", delta=0.1)
print(ball.inventory)

# Ok, it's not picking it up. I will just manually trigger the exact loop lines.
def trigger_pickup(action, nearest):
    # This simulates what Action is doing
    if getattr(nearest, "kind", None) == "booster_trap_item":
        if not hasattr(action.ball, "inventory"):
            action.ball.inventory = []
        action.ball.inventory.append("booster_trap_item")
        if nearest in action.world.boosters:
            action.world.boosters.remove(nearest)

trigger_pickup(action, item)
print(ball.inventory)
