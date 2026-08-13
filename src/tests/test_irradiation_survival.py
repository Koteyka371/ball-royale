import pytest
from ai.game_modes import IrradiationSurvivalMode
from ai.action import Action

class DummyArena:
    def __init__(self):
        self.hazards = []

class DummyWorld:
    def __init__(self):
        self.tick = 0
        self.next_id_val = 1
        self.boosters = []
        self.arena = DummyArena()

    def next_id(self):
        self.next_id_val += 1
        return self.next_id_val

class DummyBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.radius = 15.0
        self.alive = True
        self.ball_type = "normal"
        self.max_stamina = 100.0
        self.stamina = 100.0
        self.mutation_level = 0.0
        self.mutant = False

def test_irradiation_zone_spawn_and_expand():
    world = DummyWorld()
    ball = DummyBall(1, 500, 500)
    balls = [ball]

    mode = IrradiationSurvivalMode()
    mode.setup(world, balls)

    mode.zone_timer = 0
    mode.tick(world, balls, 0.1)

    assert len(mode.irradiation_zones) == 1
    zone = mode.irradiation_zones[0]

    initial_radius = zone['radius']
    mode.tick(world, balls, 0.1)

    assert zone['radius'] > initial_radius

def test_irradiation_mutation():
    world = DummyWorld()
    ball = DummyBall(1, 500, 500)
    balls = [ball]

    mode = IrradiationSurvivalMode()
    mode.setup(world, balls)

    mode.zone_timer = 0
    mode.tick(world, balls, 0.1)

    # Place zone on ball
    zone = mode.irradiation_zones[0]
    zone['x'] = 500
    zone['y'] = 500
    zone['radius'] = 100.0

    # Mutate
    for _ in range(60):
        mode.tick(world, balls, 0.1)

    assert ball.mutation_level > 5.0
    assert ball.mutant == True
    assert ball.max_stamina < 100.0

def test_anti_radiation_booster():
    world = DummyWorld()
    ball = DummyBall(1, 500, 500)
    ball.mutation_level = 10.0
    ball.mutant = True
    ball.max_stamina = 20.0

    class DummyHazard:
        def __init__(self):
            self.id = 2
            self.x = 500
            self.y = 500
            self.radius = 15.0
            self.kind = 'anti_radiation_booster'
            self.active = True

    booster = DummyHazard()
    world.boosters.append(booster)

    class DummyAction(Action):
        def _get_boosters(self):
            return self.world.boosters
        def _idle(self, delta):
            pass

    action = DummyAction(ball, world)
    action._collect_booster(0.1)

    assert ball.mutation_level == 0.0
    assert ball.mutant == False
    assert ball.max_stamina == 100.0
    assert len(world.boosters) == 0
