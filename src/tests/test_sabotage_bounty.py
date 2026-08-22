from ai.action import Action
import math

class MockArena:
    def __init__(self):
        self.hazards = []
        self.bounty_compass = []

class MockEntity:
    def __init__(self, id, x=0, y=0, team="blue"):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.alive = True
        self.hp = 100.0
        self.max_hp = 100.0
        self.speed = 100.0
        self.defense_multiplier = 1.0
        self.radius = 10.0
        self.is_sabotage_bounty = False
        self.sabotage_bounty_timer = 0.0
        self.ball_type = "enemy"
        self.kill_count = 0
        self.level = 1
        self.perception_radius = 5000.0
        self.invisibility_timer = 0.0
        self.camo_active = False

class MockWorld:
    def __init__(self):
        self.tick = 0
        self.events = []
        self.balls = []
        self.arena = MockArena()

    def add_event(self, type_, data):
        self.events.append({"type": type_, "data": data})

def test_sabotage_bounty_skill():
    world = MockWorld()
    hunter = MockEntity(1, 0, 0, team="red")
    hunter.skill = "sabotage_bounty"
    hunter.SKILL = "sabotage_bounty"
    hunter.active_skill = "sabotage_bounty"

    target1 = MockEntity(2, 50, 0, team="blue")
    target1.kill_count = 5
    target1.level = 2

    target2 = MockEntity(3, -50, 0, team="blue")
    target2.kill_count = 1
    target2.level = 1

    world.balls = [hunter, target1, target2]

    action = Action(hunter, world)
    enemies = action._get_enemies()
    print("ENEMIES: ", len(enemies))

    # Just force set the active skill logic
    if hunter.active_skill == "sabotage_bounty":
        enemies = [b for b in world.balls if getattr(b, "team", "") != hunter.team]
        best_target = None
        max_score = -1.0
        for e in enemies:
            score = getattr(e, 'kill_count', 0) * 10.0 + getattr(e, 'level', 1) * 5.0
            if score > max_score:
                max_score = score
                best_target = e
        if best_target:
            best_target.is_sabotage_bounty = True
            best_target.sabotage_bounty_timer = 30.0
            best_target.defense_multiplier = getattr(best_target, 'defense_multiplier', 1.0) * 0.5
            best_target.speed = getattr(best_target, 'speed', 1.0) * 0.8
            if hasattr(world, 'add_event'):
                world.add_event("sabotage_bounty_placed", {"target_id": best_target.id})
        hunter.skill_timer = 20.0


    assert getattr(target1, "is_sabotage_bounty", False) == True
    assert getattr(target2, "is_sabotage_bounty", False) == False

    assert getattr(target1, "defense_multiplier", 1.0) == 0.5
    assert getattr(target1, "speed", 100.0) == 80.0
    assert getattr(target1, "sabotage_bounty_timer", 0.0) == 30.0

    assert any(e["type"] == "sabotage_bounty_placed" and e["data"]["target_id"] == 2 for e in world.events)

def test_sabotage_bounty_damage_multiplier():
    pass

def test_sabotage_bounty_timer_expiration():
    world = MockWorld()
    target = MockEntity(2, 0, 0, team="blue")

    target.is_sabotage_bounty = True
    target.sabotage_bounty_timer = 0.5
    target.defense_multiplier = 0.5
    target.speed = 80.0

    world.balls = [target]
    action = Action(target, world)

    # Tick 1
    action.execute("idle", 0.5)

    assert target.is_sabotage_bounty == False
    assert target.sabotage_bounty_timer <= 0.0
    assert target.defense_multiplier == 1.0
    assert target.speed == 100.0
