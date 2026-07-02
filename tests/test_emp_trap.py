from ai.action import Action
from ai.test_chain_lightning import MockBall, MockWorld, MockHazard

def test_emp_trap_charge_up():
    world = MockWorld()
    world.balls = [
        MockBall(1, 500, 500, team="A"),
        MockBall(2, 550, 500, team="B"),
    ]
    emp = MockHazard(1, 550, 500, 150.0, "emp_trap", 0.0)
    world.arena = type('Arena', (), {'hazards': [emp]})()

    attacker = world.balls[0]
    target = world.balls[1]

    action = Action(attacker, world)
    action._get_enemies = lambda: [b for b in world.balls if b.team != attacker.team]
    action._spawn_particles = lambda x,y,k: None
    action._spawn_skill_particles = lambda k: None

    # Test chain lightning jump to EMP
    attacker.chain_lightning_timer = 5.0
    action._attempt_damage(attacker, target)

    assert emp.charge > 0.0

    emp.charge = 100.0
    action.execute("idle", 1.0)

    assert emp.active == False
    assert world.balls[1].silence_timer >= 3.0
    assert hasattr(world.balls[1], "_chrono_slow")

test_emp_trap_charge_up()
print("Tests pass")
