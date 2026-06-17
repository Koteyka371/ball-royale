import os
import random
from ai.neural_net import NeuralNet
from ai.neural_trainer import NeuralTrainer

def test_neural_net_prediction():
    nn = NeuralNet(input_size=3, output_size=2)
    inputs = [1.0, 0.5, -0.5]
    outputs = nn.predict(inputs)

    assert len(outputs) == 2
    assert isinstance(outputs[0], float)

def test_neural_net_serialization(tmp_path):
    nn1 = NeuralNet(input_size=4, output_size=3)
    filepath = os.path.join(tmp_path, "test_net.json")

    nn1.save(filepath)
    assert os.path.exists(filepath)

    nn2 = NeuralNet(input_size=4, output_size=3)
    success = nn2.load(filepath)

    assert success is True
    assert nn1.weights == nn2.weights
    assert nn1.biases == nn2.biases

def test_neural_trainer_evolution():
    trainer = NeuralTrainer(population_size=10, input_size=5, output_size=3)
    assert len(trainer.population) == 10
    assert trainer.generation == 1

    # Mock some fitness scores
    scores = [random.uniform(0, 100) for _ in range(10)]
    scores[0] = 999.0  # Make the first one definitively the best

    best_before = trainer.get_best_network(scores)

    # Evolve
    trainer.evolve_generation(scores, mutation_rate=0.0) # Zero mutation so clones match exactly
    assert trainer.generation == 2
    assert len(trainer.population) == 10

    # Best should be preserved (Elitism)
    preserved_best = trainer.population[0]
    assert preserved_best.weights == best_before.weights
    assert preserved_best.biases == best_before.biases

def test_neural_trainer_ingest_battle_results():
    """Test simulating multiple generations of training to verify learning logic."""
    trainer = NeuralTrainer(population_size=20, input_size=5, output_size=3)

    # Function to simulate a battle where a specific output is desired
    def evaluate_fitness(net):
        # Let's say optimal behavior is to output a high value for index 1
        # given input [1, 1, 1, 1, 1]
        inputs = [1.0, 1.0, 1.0, 1.0, 1.0]
        outputs = net.predict(inputs)
        return outputs[1]  # The higher this value, the better the fitness

    initial_best_score = -9999.0
    for net in trainer.population:
        score = evaluate_fitness(net)
        if score > initial_best_score:
            initial_best_score = score

    # Train for 50 generations
    for _ in range(50):
        scores = [evaluate_fitness(net) for net in trainer.population]
        trainer.evolve_generation(scores, mutation_rate=0.1, mutation_amount=0.2)

    final_scores = [evaluate_fitness(net) for net in trainer.population]
    final_best_score = max(final_scores)

    # The network should have improved over generations
    assert final_best_score >= initial_best_score
