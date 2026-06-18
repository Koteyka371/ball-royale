import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from ai.genetics import BallGenetics

class MockBall:
    def __init__(self, speed, damage, max_hp, color, skill, ball_type):
        self.speed = speed
        self.damage = damage
        self.max_hp = max_hp
        self.color = color
        self.skill = skill
        self.ball_type = ball_type

def test_extract_dna():
    genetics = BallGenetics()
    ball = MockBall(2.5, 20.0, 150.0, "red", "dash", "warrior")
    dna = genetics.extract_dna(ball)

    assert dna["speed"] == 2.5
    assert dna["damage"] == 20.0
    assert dna["max_hp"] == 150.0
    assert dna["color"] == "red"
    assert dna["skill"] == "dash"
    assert dna["ball_type"] == "warrior"

def test_register_survivors():
    genetics = BallGenetics()
    ball1 = MockBall(2.5, 20.0, 150.0, "red", "dash", "warrior")
    ball2 = MockBall(3.0, 10.0, 100.0, "blue", "shield", "tank")

    genetics.register_survivors([ball1, ball2])

    assert len(genetics.population_history) == 2

    # Register ball1 again
    genetics.register_survivors([ball1])
    assert len(genetics.population_history) == 2

    hash1 = genetics._generate_dna_hash(genetics.extract_dna(ball1))
    assert genetics.population_history[hash1]["survivals"] == 2

def test_generate_offspring_empty():
    genetics = BallGenetics()
    offspring = genetics.generate_offspring(5)
    assert len(offspring) == 0

def test_generate_offspring_fallback():
    genetics = BallGenetics(battles_to_reproduce=5)
    ball1 = MockBall(2.5, 20.0, 150.0, "red", "dash", "warrior")
    ball2 = MockBall(3.0, 10.0, 100.0, "blue", "shield", "tank")

    genetics.register_survivors([ball1])
    genetics.register_survivors([ball1]) # 2 survivals, not enough for 5
    genetics.register_survivors([ball2]) # 1 survival

    # It should fallback to top 20% since none meet the 5-battle requirement
    offspring = genetics.generate_offspring(3)
    assert len(offspring) == 3

    # Because ball1 has 2 survivals and ball2 has 1, ball1 is the top survivor
    # However since population history has 2 items, 20% is 0.4 -> max(1, 0.4) = 1
    # Only ball1 should be chosen
    assert offspring[0]["ball_type"] == "warrior" or offspring[0]["ball_type"] == "warrior_evolved"

def test_generate_offspring_eligible():
    genetics = BallGenetics(battles_to_reproduce=2)
    ball1 = MockBall(2.5, 20.0, 150.0, "red", "dash", "warrior")
    ball2 = MockBall(3.0, 10.0, 100.0, "blue", "shield", "tank")

    genetics.register_survivors([ball1])
    genetics.register_survivors([ball1]) # 2 survivals, eligible
    genetics.register_survivors([ball2]) # 1 survival, not eligible

    offspring = genetics.generate_offspring(5)
    assert len(offspring) == 5
    for child in offspring:
        assert child["ball_type"] == "warrior" or child["ball_type"] == "warrior_evolved"

def test_mutate():
    # Force 100% mutation rate to test changes
    genetics = BallGenetics(mutation_rate=1.0, mutation_amount=0.5)
    dna = {
        "speed": 2.0,
        "damage": 15.0,
        "max_hp": 100.0,
        "color": "red",
        "skill": "dash",
        "ball_type": "warrior"
    }

    child = genetics.mutate(dna)

    # At least one stat should be different
    assert (
        child["speed"] != dna["speed"] or
        child["damage"] != dna["damage"] or
        child["max_hp"] != dna["max_hp"] or
        child["color"] != dna["color"] or
        child["skill"] != dna["skill"]
    )

    # Should append _evolved
    if child != dna:
        assert child["ball_type"] == "warrior_evolved"
