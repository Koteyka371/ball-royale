from ai.kinetic_battery import KineticBatteryMode

class MockArena:
    def __init__(self):
        self.width = 800
        self.height = 600

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, name, data):
        self.events.append((name, data))

class MockBall:
    def __init__(self, team="A"):
        self.alive = True
        self.ball_type = "normal"
        self.team = team
        self.damage = 10.0
        self.hp = 100.0
        self.x = 400.0
        self.y = 300.0
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 15.0
        self.kinetic_charge = 0.0

def test_kinetic_battery_no_damage():
    mode = KineticBatteryMode()
    world = MockWorld()
    b1 = MockBall()
    mode.setup(world, [b1])

    mode.tick(world, [b1], delta=1.0)
    assert b1.damage == 0.0

def test_kinetic_battery_move_charge():
    mode = KineticBatteryMode()
    world = MockWorld()
    b1 = MockBall()
    b1.vx = 100.0
    mode.setup(world, [b1])

    mode.tick(world, [b1], delta=1.0)
    assert b1.kinetic_charge > 0.0

def test_kinetic_battery_bounce_charge():
    mode = KineticBatteryMode()
    world = MockWorld()
    b1 = MockBall()
    b1.x = 10.0
    b1.vx = 10.0
    b1.meta_prev_vx = -10.0
    mode.setup(world, [b1])

    mode.tick(world, [b1], delta=1.0)
    assert b1.kinetic_charge >= 20.0

def test_kinetic_battery_shockwave():
    mode = KineticBatteryMode()
    world = MockWorld()
    b1 = MockBall(team="A")
    b1.kinetic_charge = 99.0
    b1.vx = 100.0 # will push it over 100

    enemy = MockBall(team="B")
    enemy.x = b1.x + 50.0

    ally = MockBall(team="A")
    ally.x = b1.x + 50.0

    far_enemy = MockBall(team="B")
    far_enemy.x = b1.x + 500.0

    balls = [b1, enemy, ally, far_enemy]
    mode.setup(world, balls)

    mode.tick(world, balls, delta=1.0)

    assert b1.kinetic_charge < 100.0
    assert enemy.hp <= 0.0
    assert enemy.alive == False
    assert ally.hp == 100.0
    assert far_enemy.hp == 100.0

    explosion_events = [e for e in world.events if e[0] == "explosion"]
    assert len(explosion_events) == 1
