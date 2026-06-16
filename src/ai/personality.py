from typing import Dict

class Personality:
    """
    Defines the character of a ball and its decision modifiers.
    Available characters: aggressive, cautious, supportive, reckless, cunning.
    """
    def __init__(self, character: str = "idle"):
        self.character = character

    def get_decision_modifiers(self) -> Dict[str, float]:
        mods = {
            "flee": 0.0,
            "defend": 0.0,
            "collect_booster": 0.0,
            "attack": 0.0,
            "chase": 0.0,
            "use_skill": 0.0,
            "idle": 0.0
        }

        if self.character == "aggressive":
            mods["attack"] += 20.0
            mods["chase"] += 15.0
            mods["flee"] -= 10.0
        elif self.character == "cautious":
            mods["flee"] += 20.0
            mods["defend"] += 15.0
            mods["chase"] -= 10.0
        elif self.character == "supportive":
            mods["defend"] += 20.0
            mods["attack"] -= 5.0
            mods["chase"] -= 5.0
        elif self.character == "reckless":
            mods["attack"] += 30.0
            mods["chase"] += 25.0
            mods["flee"] -= 50.0
            mods["defend"] -= 20.0
        elif self.character == "cunning":
            mods["collect_booster"] += 20.0
            mods["chase"] += 20.0
            mods["defend"] -= 10.0

        return mods

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            return self.character == other
        if isinstance(other, Personality):
            return self.character == other.character
        return False

    def __hash__(self) -> int:
        return hash(self.character)

    def __repr__(self) -> str:
        return f"Personality('{self.character}')"

    def __str__(self) -> str:
        return self.character
