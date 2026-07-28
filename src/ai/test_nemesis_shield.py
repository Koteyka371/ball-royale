from ai.action import Action

class MockEntity:
    def __init__(self, id, x, y, kind="", radius=15.0, ball_type=None, hp=100.0, team=None):
        self.id = id
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = radius
        self.ball_type = ball_type
        self.hp = hp
        self.max_hp = hp
        self.speed = 2.0
        self.base_speed = 2.0
        self.vx = 0.0
        self.vy = 0.0
        self.team = team
        self.damage = 10.0

class MockProfileManager:
    # In real code: is_nemesis(killer, victim)
    def is_nemesis(self, killer_type, victim_type):
        return killer_type == "nemesis" and victim_type == "player"
    def get_enforcer_pledge(self, ball_type):
        return None

class MockWorld:
    def __init__(self):
        self.profile_manager = MockProfileManager()
        self.balls = []
    def _deal_damage(self, attacker, target):
        target.hp -= attacker.damage

def test_nemesis_shield():
    world = MockWorld()
    player = MockEntity(1, 0, 0, ball_type="player")
    nemesis = MockEntity(2, 0, 0, ball_type="nemesis")
    other = MockEntity(3, 0, 0, ball_type="other")
    world.balls = [player, nemesis, other]

    player.nemesis_shield_active = True

    action = Action(nemesis, world)

    # Nemesis attacks player, shield blocks it (killer=nemesis, victim=player -> True)
    action._attempt_damage(nemesis, player)
    assert player.hp == 100.0
    assert getattr(player, "nemesis_shield_active", False) == False

    # Reset shield
    player.nemesis_shield_active = True

    # Other attacks player, shield ignores it
    action = Action(other, world)
    action._attempt_damage(other, player)
    assert player.hp < 100.0
    assert getattr(player, "nemesis_shield_active", False) == True

def test_nemesis_shield_reverse_not_blocked():
    world = MockWorld()
    player = MockEntity(1, 0, 0, ball_type="player")
    nemesis = MockEntity(2, 0, 0, ball_type="nemesis")
    world.balls = [player, nemesis]

    # Shield active on nemesis
    nemesis.nemesis_shield_active = True

    action = Action(player, world)
    # Player attacks nemesis
    # is_nemesis(killer=player, victim=nemesis) -> False
    # is_nemesis(killer=nemesis, victim=player) -> True
    # The shield should NOT block the damage, because the shield is on `nemesis`, and `player` is not the nemesis of `nemesis`.

    action._attempt_damage(player, nemesis)
    assert nemesis.hp < 100.0
    assert getattr(nemesis, "nemesis_shield_active", False) == True

if __name__ == "__main__":
    test_nemesis_shield()
    test_nemesis_shield_reverse_not_blocked()
