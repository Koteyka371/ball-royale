from src.ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.tick = 1

    def _deal_damage(self, attacker, target, dmg=None):
        if dmg is None: dmg = getattr(attacker, "damage", 10.0)
        if hasattr(target, "take_damage"): target.take_damage(dmg)
        elif hasattr(target, "hp"): target.hp -= dmg
        if hasattr(target, "hp") and target.hp <= 0: target.alive = False

class MockBall:
    def __init__(self, hp, max_hp, team):
        self.hp = hp
        self.max_hp = max_hp
        self.team = team
        self.alive = True
        self.x = 0
        self.y = 0
        self.radius = 10.0
        self.id = 1
        self.speed = 10.0

class MockHazard:
    def __init__(self, team, x, y, kind):
        self.team = team
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = 100.0
        self.damage = 10.0
        self.active = True

world = MockWorld()
ball_enemy = MockBall(5, 100, "team_a")
hazard = MockHazard("team_b", 0, 0, "vampiric_puddle")
world.arena.hazards = [hazard]
world.balls = [ball_enemy]

action1 = Action(ball_enemy, world)
action1.execute('idle', 1.0)
print(f"Enemy HP: {ball_enemy.hp}, Alive: {ball_enemy.alive}")
