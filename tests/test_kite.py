from ai.ball_types_sniper import Sniper

class MockTarget:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def test_sniper_kite_too_close():
    sniper = Sniper(1, 0.0, 0.0)
    target = MockTarget(50.0, 0.0)
    delta = 0.1

    # Target is too close (dist=50 < safe_dist=120)
    sniper.skill_timer = 10.0 # Disable skill
    sniper.attack_timer = 10.0 # Disable attack

    initial_x = sniper.x
    sniper.kite(delta, target)

    assert sniper.current_action == "kite"
    # Should move away from target (target is at x=50, sniper is at x=0 -> sniper should move to -x)
    assert sniper.x < initial_x

def test_sniper_kite_too_far():
    sniper = Sniper(1, 0.0, 0.0)
    target = MockTarget(200.0, 0.0)
    delta = 0.1

    # Target is too far (dist=200 > attack_range=150)
    sniper.skill_timer = 10.0 # Disable skill
    sniper.attack_timer = 10.0 # Disable attack

    initial_x = sniper.x
    sniper.kite(delta, target)

    assert sniper.current_action == "kite"
    # Should move towards target (target is at x=200, sniper is at x=0 -> sniper should move to +x)
    assert sniper.x > initial_x

def test_sniper_kite_use_skill():
    sniper = Sniper(1, 0.0, 0.0)
    target = MockTarget(130.0, 0.0) # Within attack range (150) but > safe_dist (120)
    delta = 0.1

    sniper.skill_timer = 0.0 # Skill is ready
    sniper.kite(delta, target)

    # Should use skill
    assert sniper.current_action == "use_skill"
    assert sniper.skill_timer > 0.0

def test_sniper_kite_attack():
    sniper = Sniper(1, 0.0, 0.0)
    target = MockTarget(130.0, 0.0) # Within attack range (150) but > safe_dist (120)
    delta = 0.1

    sniper.skill_timer = 10.0 # Skill is not ready
    sniper.attack_timer = 0.0 # Attack is ready
    sniper.kite(delta, target)

    # Should attack
    assert sniper.current_action == "attack"
    assert sniper.attack_timer > 0.0
