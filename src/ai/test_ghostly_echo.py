import pytest
import sys
sys.path.append('src')
from ai.action import Action

class MockBall:
    def __init__(self, id, x, y, team):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.damage = 10.0
        self.skill = "ghostly_echo"
        self.skill_timer = 0.0
        self.SKILL_COOLDOWN = 5.0
        self.ghostly_echo_active = False
        self.ghostly_echo_data = {}

    def use_skill(self):
        pass

class MockWorld:
    def __init__(self):
        self.balls = []
        self.events = []

    def _deal_damage(self, attacker, target):
        target.hp -= attacker.damage
        if target.hp <= 0:
            target.alive = False

    def get_nearby_entities(self, ball, radius):
        return {"enemies": [b for b in self.balls if b.team != ball.team], "allies": [b for b in self.balls if b.team == ball.team]}

def test_ghostly_echo_manual_trigger():
    world = MockWorld()
    ball = MockBall(1, 100.0, 100.0, "team1")
    enemy = MockBall(2, 110.0, 110.0, "team2")
    world.balls = [ball, enemy]

    action = Action(ball, world)

    # Press 1: Place echo
    ball.skill_timer = 0.0
    action._use_skill()

    assert ball.ghostly_echo_active is True
    assert ball.ghostly_echo_data["x"] == 100.0
    assert ball.ghostly_echo_data["y"] == 100.0

    # Move ball away and take damage
    ball.x = 200.0
    ball.y = 200.0
    old_hp = ball.hp
    ball.hp -= 20.0 # Simulating damage

    # Use action to process damage
    enemy.damage = 20.0
    action._attempt_damage(enemy, ball)

    assert ball.ghostly_echo_data["damage_taken"] == 20.0

    # Press 2: Trigger echo
    ball.skill_timer = 0.0
    action._use_skill()

    assert ball.ghostly_echo_active is False
    assert ball.x == 100.0
    assert ball.y == 100.0
    assert enemy.hp == 100.0 - (20.0 * 1.5) # Enemy took shockwave damage
    assert any(e["type"] == "visual_effect" and e["data"]["type"] == "shockwave" for e in world.events)

def test_ghostly_echo_lethal_damage():
    world = MockWorld()
    ball = MockBall(1, 100.0, 100.0, "team1")
    enemy = MockBall(2, 110.0, 110.0, "team2")
    world.balls = [ball, enemy]

    action = Action(ball, world)

    # Place echo
    ball.skill_timer = 0.0
    action._use_skill()

    # Move ball
    ball.x = 200.0
    ball.y = 200.0

    # Take lethal damage
    enemy.damage = 150.0
    # In action.py, the _attempt_damage calculates old_hp at the top
    # But wait, _deal_damage is called inside _attempt_damage
    # For a basic attack, it falls through to the end of _attempt_damage where self.world._deal_damage(attacker, target) is called
    action._attempt_damage(enemy, ball)

    # Should survive with 1 HP
    assert ball.hp == 1.0
    assert ball.alive is True

    # Should teleport back
    assert ball.x == 100.0
    assert ball.y == 100.0
    assert ball.ghostly_echo_active is False

    # Shockwave should have damaged enemy
    # Total damage taken since echo was 0 originally + 100 (since max health is 100, wait, old_hp was 100, new_hp was -50 => 100 - (-50) = 150)
    expected_shockwave_damage = 150.0 * 1.5
    assert enemy.hp == 100.0 - expected_shockwave_damage
