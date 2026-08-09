from ai.action import Action
from types import SimpleNamespace

class MockBall(SimpleNamespace):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not hasattr(self, 'id'): self.id = 1
        if not hasattr(self, 'x'): self.x = 0.0
        if not hasattr(self, 'y'): self.y = 0.0
        if not hasattr(self, 'vx'): self.vx = 0.0
        if not hasattr(self, 'vy'): self.vy = 0.0
        if not hasattr(self, 'hp'): self.hp = 100.0
        if not hasattr(self, 'max_hp'): self.max_hp = 100.0

class MockWorld(SimpleNamespace):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not hasattr(self, 'balls'): self.balls = []
        if not hasattr(self, 'next_id'): self.next_id = 100

def test_clan_banner_deploy():
    ball = MockBall(skill="deploy_clan_banner", skill_timer=0, active_skill="deploy_clan_banner")
    world = MockWorld(balls=[ball])

    action = Action(ball, world)
    action._use_skill()

    assert len(world.balls) == 2, "Clan banner was not deployed"
    banner = world.balls[1]
    assert getattr(banner, "is_clan_banner", False) == True, "Banner flag missing"
    assert getattr(banner, "is_decoy", False) == True, "Banner decoy flag missing"
    assert getattr(banner, "clan_banner_timer", 0) > 0, "Banner timer not set"

def test_clan_banner_healing():
    banner = MockBall(id=2, owner_id=1, is_clan_banner=True, clan_banner_timer=10.0, alive=True)
    ally = MockBall(id=1, owner_id=1, hp=50.0, max_hp=100.0, alive=True)
    world = MockWorld(balls=[banner, ally])

    action = Action(banner, world)
    action.execute('idle', 1.0)

    # 1.0 second should heal 15.0 HP
    assert ally.hp == 65.0, f"Ally HP should be 65.0, but got {ally.hp}"
    assert banner.clan_banner_timer == 9.0, f"Timer should be 9.0, got {banner.clan_banner_timer}"

def test_clan_banner_death():
    banner = MockBall(id=2, owner_id=1, is_clan_banner=True, clan_banner_timer=0.5, alive=True, hp=100.0)
    world = MockWorld(balls=[banner])

    action = Action(banner, world)
    action.execute('idle', 1.0)

    # Timer drops below 0, should die
    assert banner.clan_banner_timer == -0.5
    assert not banner.alive
    assert banner.hp == 0

if __name__ == '__main__':
    test_clan_banner_deploy()
    test_clan_banner_healing()
    test_clan_banner_death()
    print("All Clan Banner tests passed!")
