import random
import copy
from typing import Dict, List, Any

class BallGenetics:
    """
    Handles genetics and reproduction of balls across multiple simulations.
    Balls that survive N battles can reproduce.
    Offspring inherit traits (speed, damage, max_hp, color, skill) with random mutations.
    """

    def __init__(self, battles_to_reproduce: int = 3, mutation_rate: float = 0.1, mutation_amount: float = 0.15):
        self.battles_to_reproduce = battles_to_reproduce
        self.mutation_rate = mutation_rate
        self.mutation_amount = mutation_amount

        # Track survival counts and stats for balls across generations.
        # Format: { "dna_hash": {"survivals": int, "dna": dict} }
        self.population_history: Dict[str, Dict[str, Any]] = {}

        # Color palettes for mutation
        self.colors = [
            "red", "gray", "purple", "green", "blue", "orange", "crimson", "darkred",
            "cyan", "brown", "lime", "gold", "lightblue", "black", "white", "pink", "yellow"
        ]

        self.skills = [
            "wave_attack", "shield", "dash", "health_link", "precision_shot",
            "explosion", "rage_burst", "ground_pound", "phase_through",
            "steal_boost", "clone", "protect_ally", "command", "stealth", "summon_minions"
        ]

    def _generate_dna_hash(self, dna: Dict[str, Any]) -> str:
        """Generates a unique but repeatable hash for a set of DNA traits."""
        # Round numerical values to prevent floating point drift from creating infinite hashes
        rounded_dna = {}
        for k, v in dna.items():
            if isinstance(v, float):
                rounded_dna[k] = round(v, 2)
            else:
                rounded_dna[k] = v

        # Create a string representation sorted by key
        hash_str = "-".join([f"{k}:{rounded_dna[k]}" for k in sorted(rounded_dna.keys())])
        return hash_str

    def extract_dna(self, ball: Any) -> Dict[str, Any]:
        """Extracts the genetic traits from a ball instance."""
        return {
            "speed": getattr(ball, "speed", 2.0),
            "damage": getattr(ball, "damage", 15.0),
            "max_hp": getattr(ball, "max_hp", 100.0),
            "color": getattr(ball, "color", "red"),
            "skin": getattr(ball, "skin", "default"),
            "skill": getattr(ball, "skill", "dash"),
            "skill_cooldown": getattr(ball, "skill_cooldown", 5.0),
            "ball_type": getattr(ball, "ball_type", "unknown")
        }

    def register_survivors(self, survivors: List[Any]):
        """Records balls that survived a battle."""
        for ball in survivors:
            dna = self.extract_dna(ball)
            dna_hash = self._generate_dna_hash(dna)

            if dna_hash not in self.population_history:
                self.population_history[dna_hash] = {
                    "survivals": 1,
                    "dna": dna
                }
            else:
                self.population_history[dna_hash]["survivals"] += 1

    def generate_offspring(self, count: int) -> List[Dict[str, Any]]:
        """
        Produces new offspring DNA from balls that have survived enough battles.
        If not enough parents are eligible, it falls back to the top survivors.
        """
        eligible_parents = []
        for hash_val, data in self.population_history.items():
            if data["survivals"] >= self.battles_to_reproduce:
                # Add multiple entries if they survived many times (higher fitness)
                weight = max(1, data["survivals"] - self.battles_to_reproduce + 1)
                eligible_parents.extend([data["dna"]] * weight)

        # Fallback if no parents are fully eligible yet
        if not eligible_parents:
            # Sort by survivals descending
            sorted_history = sorted(
                self.population_history.values(),
                key=lambda x: x["survivals"],
                reverse=True
            )
            # Take top 20%
            top_count = max(1, int(len(sorted_history) * 0.2))
            eligible_parents = [data["dna"] for data in sorted_history[:top_count]]

        # If still empty (e.g., very first generation without input), return empty
        if not eligible_parents:
            return []

        offspring = []
        for _ in range(count):
            parent_dna = random.choice(eligible_parents)
            child_dna = self.mutate(parent_dna)

            # Apply skin based on survivals of the parent it came from
            survivals = 0
            for hash_v, d in self.population_history.items():
                if d["dna"] == parent_dna:
                    survivals = d["survivals"]
                    break
            if survivals >= 10:
                child_dna["skin"] = "legendary"
            elif survivals >= 5:
                child_dna["skin"] = "elite"
            elif survivals >= 3:
                child_dna["skin"] = "veteran"
            else:
                child_dna["skin"] = "default"

            offspring.append(child_dna)

        return offspring

    def mutate(self, dna: Dict[str, Any]) -> Dict[str, Any]:
        """Applies random mutations to a DNA string."""
        child = copy.deepcopy(dna)

        # Mutate numerical stats
        for stat in ["speed", "damage", "max_hp", "skill_cooldown"]:
            if stat in child and random.random() < self.mutation_rate:
                # Multiply by a factor between (1 - mutation_amount) and (1 + mutation_amount)
                factor = 1.0 + random.uniform(-self.mutation_amount, self.mutation_amount)
                child[stat] *= factor

                # Enforce minimums
                if stat == "speed":
                    child[stat] = max(0.5, child[stat])
                elif stat == "damage":
                    child[stat] = max(1.0, child[stat])
                elif stat == "max_hp":
                    child[stat] = max(10.0, child[stat])
                elif stat == "skill_cooldown":
                    child[stat] = max(1.0, child[stat])

        # Mutate color
        if "color" in child and random.random() < (self.mutation_rate * 0.5):
            child["color"] = random.choice(self.colors)

        # Mutate skill
        if "skill" in child and random.random() < (self.mutation_rate * 0.2):
            child["skill"] = random.choice(self.skills)

        # If a mutation happens, append a marker to ball_type to indicate it's evolved
        if child != dna and not child["ball_type"].endswith("_evolved"):
             child["ball_type"] = f"{child['ball_type']}_evolved"

        return child
