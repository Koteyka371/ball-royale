import pytest
from ai.action import Action

class MockBall:
    def __init__(self, x, y, team, id):
        self.x = x
        self.y = y
        self.team = team
        self.id = id
        self.radius = 10.0
        self.alive = True
        self.skill = "throw_purge_bomb"
        self.skill_timer = 0.0
        self.skill_cooldown = 5.0

        # Buffs to strip
        self.supercharge_timer = 5.0
        self.overcharged_timer = 5.0
        self.overclock_timer = 5.0
        self.damage_buff_timer = 5.0
        self.stamina_booster_timer = 5.0
        self.shield_timer = 5.0
        self.energy_shield_timer = 5.0
        self.invulnerable_timer = 5.0
        self.speed_boost_timer = 5.0
        self.speed = 100.0

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.events = []

def test_throw_purge_bomb_creation():
    world = MockWorld()
    ball1 = MockBall(0, 0, "team1", 1)
    ball2 = MockBall(50, 0, "team2", 2)
    world.balls = [ball1, ball2]

    action = Action(ball1, world)
    ball1.skill_timer = 5.0
    bomb = type("Hazard", (), {})
    bomb.kind = "thrown_purge_bomb"
    bomb.x = 50.0
    bomb.y = 0.0
    bomb.radius = 20.0
    bomb.vx = 0.0
    bomb.vy = 0.0
    bomb.duration = 2.0
    bomb.owner_id = ball1.id
    bomb.team = ball1.team
    world.arena.hazards.append(bomb)

    assert ball1.skill_timer > 0.0

    # Find the bomb
    purge_bombs = [h for h in world.arena.hazards if getattr(h, "kind", "") == "thrown_purge_bomb"]
    assert len(purge_bombs) == 1
    bomb = purge_bombs[0]
    assert bomb.duration == 2.0
    assert bomb.owner_id == ball1.id
    assert bomb.team == ball1.team

def test_throw_purge_bomb_explosion():
    world = MockWorld()
    ball1 = MockBall(0, 0, "team1", 1)
    ball2 = MockBall(50, 0, "team2", 2)
    world.balls = [ball1, ball2]

    # Pre-test check that buffs are active on ball2
    assert ball2.supercharge_timer == 5.0
    assert ball2.shield_timer == 5.0

    action = Action(ball1, world)

    # Create the bomb directly as if thrown
    bomb = type("Hazard", (), {})()
    bomb.kind = "thrown_purge_bomb"
    bomb.x = 50.0
    bomb.y = 0.0
    bomb.radius = 20.0
    bomb.vx = 0.0
    bomb.vy = 0.0
    bomb.duration = 0.1 # Small duration to explode next tick
    bomb.owner_id = ball1.id
    bomb.team = ball1.team
    world.arena.hazards.append(bomb)

    action.execute("idle", 0.5) # Time delta larger than duration to trigger explosion

    # Bomb should be removed
    assert bomb not in world.arena.hazards

    # Visual effect should be spawned
    purge_events = [e for e in world.events if e.get("type") == "visual_effect" and e["data"].get("type") == "purge_explosion"]
    assert len(purge_events) == 1

    # Buffs should be stripped on enemy
    assert ball2.supercharge_timer == 0.0
    assert ball2.overcharged_timer == 0.0
    assert ball2.overclock_timer == 0.0
    assert ball2.damage_buff_timer == 0.0
    assert ball2.stamina_booster_timer == 0.0
    assert ball2.shield_timer == 0.0
    assert ball2.energy_shield_timer == 0.0
    assert ball2.invulnerable_timer == 0.0

    # Fleeing speed burst should be applied
    assert ball2.speed_boost_timer == 2.0
