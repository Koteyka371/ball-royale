from ai.action import Action

class MockWorld:
    def __init__(self):
        self.balls = []
        self.events = []
        self.tick = 1

class MockBall:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        if not hasattr(self, "id"): self.id = 1
        if not hasattr(self, "x"): self.x = 0.0
        if not hasattr(self, "y"): self.y = 0.0
        if not hasattr(self, "alive"): self.alive = True

        # Initialize required base stats for Action execution
        self._base_speed_set = True
        self.base_speed = 100.0
        self.base_damage = 10.0
        self.speed_multiplier = 1.0
        self.damage_multiplier = 1.0

def test_decoy_mimic_cast():
    world = MockWorld()

    owner = MockBall(id=1, has_decoy_mimic_cast=True, active_skill="fireball")
    decoy = MockBall(id=2, owner_id=1, is_decoy=True, x=100.0, y=100.0, decoy_mimic_cast_timer=1.0, decoy_timer=10.0)

    world.balls = [owner, decoy]

    action = Action(decoy, world)

    # Tick past the timer
    action.execute("idle", 2.0)

    assert len(world.events) == 1
    assert world.events[0]['type'] == 'visual_effect'
    assert world.events[0]['data']['type'] == 'skill_cast_mimic'
    assert world.events[0]['data']['skill'] == 'fireball'
    assert world.events[0]['data']['x'] == 100.0

def test_decoy_mimic_cast_from_traits():
    world = MockWorld()

    owner = MockBall(id=1, traits=["decoy_mimic_cast"], skill="frost_nova")
    decoy = MockBall(id=2, mimic_owner=1, is_decoy_clone=True, x=50.0, y=50.0, decoy_mimic_cast_timer=0.5, decoy_timer=10.0)

    world.balls = [owner, decoy]

    action = Action(decoy, world)

    # Tick past the timer
    action.execute("idle", 1.0)

    assert len(world.events) == 1
    assert world.events[0]['type'] == 'visual_effect'
    assert world.events[0]['data']['type'] == 'skill_cast_mimic'
    assert world.events[0]['data']['skill'] == 'frost_nova'
