import pytest
from ai.action import Action
import random
import copy

class MockEntity:
    def __init__(self, id, x, y, team="team1"):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.ball_type = team
        self.hp = 100
        self.max_hp = 100
        self.radius = 10
        self.alive = True
        self.is_dashing = False

class MockWorld:
    def __init__(self):
        self.balls = []
        self.events = []
        self.next_id = 1000

class MockArena:
    def clamp_position(self, x, y, radius):
        return x, y, False

def test_cluster_dash_success_spawn_mirages():
    world = MockWorld()
    world.arena = MockArena()

    ball = MockEntity(1, 100, 100, team="team1")
    ball.active_skill_name = "dash"
    ball.damage = 10
    ball.skill_timer = 0
    ball.active_skill = None
    ball.is_dashing = False
    world.balls.append(ball)

    # Spawn 3 enemies close together
    e1 = MockEntity(2, 120, 100, team="team2")
    e2 = MockEntity(3, 140, 100, team="team2")
    e3 = MockEntity(4, 160, 100, team="team2")

    world.balls.extend([e1, e2, e3])

    action = Action(ball, world)

    # execute dash
    action.ball.skill = "dash"
    action.ball.SKILL = "dash"
    action.ball.active_skill = "dash"
    action.ball.active_skill_name = "dash"
    action.ball.skill_timer = 0
    action.world.arena.clamp_position = lambda x, y, r: (x, y, False)

    action._use_skill()
    print([b.decoy_type for b in action.world.balls if hasattr(b, 'decoy_type')])
    print([b.is_decoy for b in action.world.balls if hasattr(b, 'is_decoy')])

    # After a successful 3 jump dash, there should be 3 static mirages in world.balls
    mirages = [b for b in world.balls if getattr(b, "is_decoy", False) and getattr(b, "decoy_type", "") == "static_mirage"]
    assert len(mirages) == 3, f"Expected 3 mirages, got {len(mirages)}"

    for m in mirages:
        assert m.hp == 1.0
        assert m.max_hp == 1.0
        assert m.decoy_timer == 2.0
        assert getattr(m, "vx", -1) == 0.0
        assert getattr(m, "vy", -1) == 0.0
        assert getattr(m, "speed", -1) == 0.0
