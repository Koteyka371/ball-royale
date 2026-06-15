from dataclasses import dataclass
from typing import Dict

@dataclass
class Personality:
    character: str  # aggressive, cautious, supportive, reckless, cunning

    def get_decision_modifiers(self) -> Dict[str, float]:
        modifiers = {
            "attack": 0.0,
            "flee": 0.0,
            "defend": 0.0,
            "chase": 0.0,
            "collect_booster": 0.0,
            "use_skill": 0.0,
        }

        if self.character == "aggressive":
            modifiers["attack"] = 30.0
            modifiers["chase"] = 30.0
            modifiers["flee"] = -20.0
        elif self.character == "cautious":
            modifiers["defend"] = 30.0
            modifiers["flee"] = 20.0
            modifiers["attack"] = -10.0
            modifiers["chase"] = -10.0
        elif self.character == "supportive":
            modifiers["defend"] = 20.0
            modifiers["use_skill"] = 20.0
        elif self.character == "reckless":
            modifiers["attack"] = 40.0
            modifiers["chase"] = 40.0
            modifiers["flee"] = -50.0
            modifiers["defend"] = -20.0
        elif self.character == "cunning":
            modifiers["collect_booster"] = 40.0
            modifiers["flee"] = 10.0
            modifiers["attack"] = -10.0

        return modifiers

def get_default_personality(ball_type: str) -> Personality:
    mapping = {
        "assassin": "aggressive",
        "berserker": "reckless",
        "bomber": "reckless",
        "guardian": "cautious",
        "healer": "supportive",
        "juggernaut": "cautious",
        "phantom": "cunning",
        "rogue": "cunning",
        "sniper": "cautious",
        "swarm": "aggressive",
        "tank": "cautious",
        "warrior": "aggressive"
    }
    return Personality(mapping.get(ball_type, "cautious"))
