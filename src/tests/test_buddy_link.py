import pytest
from ai.action import Action

class MockBall:
    def __init__(self, id, x, y, team, cosmetic=""):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.cosmetic = cosmetic
        self.alive = True
        self.radius = 10.0
        self.mass = 1.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

    def get_nearby_entities(self, ball, radius):
        nearby = []
        for b in self.arena.balls:
            if b.id != ball.id:
                dist = ((b.x - ball.x)**2 + (b.y - ball.y)**2)**0.5
                if dist < radius:
                    nearby.append(b)
        return nearby

class MockArena:
    def __init__(self):
        self.balls = []

def test_buddy_link_knockback_shared():
    # Setup
    world = MockWorld()
    # p1 and p2 are allies. p3 is an enemy that bumps into p1
    p1 = MockBall(1, 100, 100, "team1", "buddy_link")
    p2 = MockBall(2, 120, 120, "team1")
    p3 = MockBall(3, 105, 105, "team2")

    world.arena.balls = [p1, p2, p3]

    action = Action(p1, world)

    action._resolve_collisions()

    # Normally p1 would move by nx * overlap * 0.5
    # With buddy link, p1 moves by nx * overlap * 0.25
    # p2 should also move by nx * overlap * 0.25
    # Let's verify p2 moved from its starting position (120, 120)
    # The exact value is not critical, just that it moved in the negative direction

    assert p2.x < 120.0
    assert p2.y < 120.0

    # And p1 moved from 100, 100
    assert p1.x < 100.0
    assert p1.y < 100.0

def test_buddy_link_status_effect_shared():
    world = MockWorld()
    p1 = MockBall(1, 100, 100, "team1", "buddy_link")
    p1.speed_boost_timer = 5.0
    p1.energy_shield_timer = 2.0
    p1.hazard_immunity_timer = 0.0 # Not tested, but included

    p2 = MockBall(2, 150, 150, "team1")
    p2.speed_boost_timer = 1.0 # Should be overwritten to 5.0

    p3 = MockBall(3, 105, 105, "team2") # Collision target

    world.arena.balls = [p1, p2, p3]
    action = Action(p1, world)

    action._resolve_collisions()

    # Check that status effects were shared to p2
    assert getattr(p2, "speed_boost_timer", 0.0) == 5.0
    assert getattr(p2, "energy_shield_timer", 0.0) == 2.0
