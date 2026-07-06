from ai.action import Action
from ai.decision import Decision
from ai.perception import Perception

class MockBall:
    def __init__(self, id, x, y, ball_type="warrior"):
        self.id = id
        self.x = x
        self.y = y
        self.ball_type = ball_type
        self.speed = 2.0
        self.radius = 10.0
        self.hp = 100
        self.max_hp = 100
        self.damage = 10
        self.alive = True
        self.perception_radius = 250
        self.memory = {}
        self.current_action = "idle"
        self.team_message = None
        self.skill_timer = 10

class MockWorld:
    def __init__(self, balls):
        self.balls = balls

    def get_nearby_entities(self, ball, radius):
        enemies = [b for b in self.balls if b != ball and b.ball_type != ball.ball_type]
        allies = [b for b in self.balls if b != ball and b.ball_type == ball.ball_type]
        return {"enemies": enemies, "allies": allies, "boosters": [], "traps": []}

    def _deal_damage(self, attacker, target):
        target.hp -= attacker.damage

def test_rival_memory_recorded():
    attacker = MockBall(1, 0, 0, "assassin")
    target = MockBall(2, 5, 0, "warrior")
    world = MockWorld([attacker, target])
    action = Action(attacker, world)

    # Trigger attack
    action.execute("attack", 0.1)

    # Target should now have memory of attacker
    assert hasattr(target, "memory")
    assert 1 in target.memory
    assert target.memory[1]["relation"] == "rival"

def test_rival_prioritized():
    ball = MockBall(1, 0, 0, "warrior")
    rival = MockBall(2, 100, 0, "assassin")
    normal_enemy = MockBall(3, 10, 0, "tank")

    world = MockWorld([ball, rival, normal_enemy])
    action = Action(ball, world)

    # Set memory manually
    ball.memory[2] = {"relation": "rival"}

    # _get_target should prioritize rival even though normal_enemy is closer
    enemies = world.get_nearby_entities(ball, 250)["enemies"]
    target = action._get_target(enemies)

    assert target == rival

def test_rival_increases_threat_and_attack_score():
    ball = MockBall(1, 0, 0, "warrior")
    rival = MockBall(2, 50, 0, "assassin")
    world = MockWorld([ball, rival])

    ball.memory[2] = {"relation": "rival"}

    perception = Perception(ball, world)
    data = perception.scan()

    assert data["rival_spotted"] is True

    decision = Decision(ball, world)
    action_type = decision.choose_action(data, "neutral")

    # Chase or Attack should be highly scored
    assert action_type in ["attack", "chase", "flank", "ricochet_attack", "defend"]
