from typing import Dict

class Personality:
    """
    Defines the ball's character and provides decision modifiers.
    Supported characters: aggressive, cautious, supportive, reckless, cunning
    """

    def __init__(self, character: str = "idle", original_type: str = ""):
        self.character = character
        self.original_type = original_type if original_type else character

    def get_decision_modifiers(self) -> Dict[str, float]:
        modifiers = {
            "flee": 0.0,
            "defend": 0.0,
            "collect_booster": 0.0,
            "attack": 0.0,
            "chase": 0.0,
            "use_skill": 0.0,
            "idle": 0.0,
        }

        if self.character == "aggressive":
            modifiers["attack"] += 20.0
            modifiers["chase"] += 20.0
            modifiers["flee"] -= 20.0
        elif self.character == "cautious":
            modifiers["flee"] += 20.0
            modifiers["defend"] += 20.0
            modifiers["attack"] -= 10.0
            modifiers["chase"] -= 20.0
        elif self.character == "supportive":
            modifiers["defend"] += 30.0
            modifiers["use_skill"] += 10.0
        elif self.character == "reckless":
            modifiers["attack"] += 30.0
            modifiers["use_skill"] += 20.0
            modifiers["flee"] -= 50.0
            modifiers["defend"] -= 20.0
        elif self.character == "cunning":
            modifiers["collect_booster"] += 20.0
            modifiers["chase"] += 10.0
            modifiers["defend"] += 10.0

        return modifiers

    def __eq__(self, other):
        if isinstance(other, str):
            return self.character == other or self.original_type == other
        if isinstance(other, Personality):
            return self.character == other.character
        return False

    def __hash__(self):
        # We need to hash both to ensure consistency with __eq__
        # Actually if a == b implies hash(a) == hash(b), we shouldn't dynamically evaluate eq against multiple options unless we hash the same.
        # But wait! If `other` is a string "assassin", `hash("assassin")` must equal `hash(Personality("cunning", "assassin"))`!
        # This is impossible. We can't make `hash(Personality)` equal to `hash("string")` without explicitly returning `hash(self.original_type)`.
        return hash(self.original_type)

    def __str__(self):
        return self.character

    def __repr__(self):
        return f"Personality('{self.character}')"
