import random
from typing import List
from .neural_net import NeuralNet

class NeuralTrainer:
    """
    Handles the generational learning logic for the Neural Network module.
    Refines learning over multiple generations using genetic algorithms based on fitness scores.
    """

    def __init__(self, population_size: int, input_size: int, output_size: int):
        self.population_size = population_size
        self.input_size = input_size
        self.output_size = output_size
        self.population: List[NeuralNet] = []
        self.generation = 1

        self._initialize_population()

    def _initialize_population(self) -> None:
        """Create the initial population of random neural networks."""
        self.population = [NeuralNet(self.input_size, self.output_size) for _ in range(self.population_size)]

    def evolve_generation(self, fitness_scores: List[float], mutation_rate: float = 0.1, mutation_amount: float = 0.5) -> None:
        """
        Evolve the population to the next generation based on fitness scores.
        fitness_scores: List of scores corresponding to each network in self.population.
        """
        if len(fitness_scores) != self.population_size:
            raise ValueError(f"Expected {self.population_size} fitness scores, got {len(fitness_scores)}")

        # Pair each network with its fitness score
        scored_population = list(zip(self.population, fitness_scores))

        # Sort by fitness descending
        scored_population.sort(key=lambda x: x[1], reverse=True)

        # Keep top 20% directly (elitism)
        elite_count = max(1, int(self.population_size * 0.2))
        elites = [net for net, score in scored_population[:elite_count]]

        new_population = []

        # Elites pass directly to next generation
        for elite in elites:
            new_population.append(elite.clone())

# Fill the rest with crossed-over and mutated clones of elites
        while len(new_population) < self.population_size:
            parent1 = random.choice(elites)
            parent2 = random.choice(elites)
            child = parent1.crossover(parent2)
            child.mutate(rate=mutation_rate, amount=mutation_amount)
            new_population.append(child)

        self.population = new_population
        self.generation += 1

    def get_best_network(self, fitness_scores: List[float]) -> NeuralNet:
        """Returns the network with the highest fitness score."""
        scored_population = list(zip(self.population, fitness_scores))
        scored_population.sort(key=lambda x: x[1], reverse=True)
        return scored_population[0][0]

    def save_best(self, fitness_scores: List[float], filepath: str) -> None:
        """Saves the best performing network to a file."""
        best_net = self.get_best_network(fitness_scores)
        best_net.save(filepath)

    def load_population(self, filepaths: List[str]) -> None:
        """Loads a population from a list of filepaths."""
        self.population = []
        for path in filepaths:
            net = NeuralNet(self.input_size, self.output_size)
            if net.load(path):
                self.population.append(net)
            else:
                # If load fails, add a random one
                self.population.append(NeuralNet(self.input_size, self.output_size))

        # Pad if needed
        while len(self.population) < self.population_size:
            self.population.append(NeuralNet(self.input_size, self.output_size))

        # Truncate if too many
        self.population = self.population[:self.population_size]
