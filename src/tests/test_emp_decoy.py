def test_emp_decoy_skills():
    import os
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from ai.action import Action

    class MockBall:
        def __init__(self, id, team, is_decoy=False, decoy_type="", x=0, y=0, hp=100, max_hp=100):
            self.id = id
            self.team = team
            self.is_decoy = is_decoy
            self.decoy_type = decoy_type
            self.x = x
            self.y = y
            self.hp = hp
            self.max_hp = max_hp
            self.alive = True
            self.silence_timer = 0.0
            self.skill_timer = 0.0
            self.decoy_timer = 5.0
            self.owner_id = 1
            self.traits = []

    class MockWorld:
        def __init__(self, balls):
            self.balls = balls

    decoy = MockBall(1, "A", True, "emp_decoy", 100, 100, hp=0)
    enemy = MockBall(2, "B", False, "", 120, 120)
    world = MockWorld([decoy, enemy])

    action = Action(decoy, world)
    action.execute("idle", 0.1)

    assert enemy.silence_timer > 0, "Silence timer should be set"
    assert enemy.skill_timer > 0, "Skill timer should be set"
