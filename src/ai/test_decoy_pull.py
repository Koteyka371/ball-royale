from ai.action import Action
import math

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000
        self.height = 1000
    def clamp_position(self, x, y, radius):
        return x, y, False
    def update_zone(self, tick, delta):
        pass

class MockBall:
    def __init__(self, id=1, x=0, y=0):
        self.id = id
        self.hp = 100
        self.max_hp = 100
        self.alive = True
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.team = "player"
        self.ball_type = "basic"
        self.speed = 100
        self.base_speed = 100
        self.radius = 15.0
        self.skill = None
        self.active_skill = None
        self.damage = 10
        self.traits = []

class MockWorld:
    def __init__(self):
        self.balls = []
        self.tick = 0
        self.next_id = 9999
        self.arena = MockArena()

def test_decoy_explosion_poison_pull():
    world = MockWorld()
    decoy = MockBall(x=100, y=100)
    decoy.is_decoy = True
    decoy.decoy_type = "poison_cloud" # Does this type exist?
    decoy.team = "A"
    decoy.hp = 0 # Force explode
    decoy.decoy_timer = 5.0

    enemy = MockBall(x=150, y=100) # Distance 50
    enemy.team = "B"

    world.balls = [decoy, enemy]

    action = Action(decoy, world)
    action.execute("idle", 0.1)

    print(f"Enemy HP: {enemy.hp}")
    print(f"Enemy Stutter: {getattr(enemy, 'stutter_timer', 0)}")
    print(f"Enemy X: {enemy.x}, Y: {enemy.y}")
    print(f"Arena hazards: {len(world.arena.hazards)}")
    if len(world.arena.hazards) > 0:
        h = world.arena.hazards[0]
        print(f"Hazard: {getattr(h, 'kind', 'unknown')} at {h.x}, {h.y}")

if __name__ == "__main__":
    test_decoy_explosion_poison_pull()
