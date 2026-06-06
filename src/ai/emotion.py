from typing import Any, Dict

class Emotion:
    """
    Emotion system that determines the ball's emotional state based on perception.
    Evaluates states in order of precedence: Fear, Bloodlust, Heroism, Greed, Rage, Cowardice.
    """

    def __init__(self, ball: Any):
        self.ball = ball

    def process(self, perception_data: Dict[str, Any]) -> str:
        hp_percent = 1.0
        if hasattr(self.ball, "get_hp_percent"):
            hp_percent = self.ball.get_hp_percent()
        elif hasattr(self.ball, "hp") and hasattr(self.ball, "max_hp"):
            hp_percent = float(self.ball.hp) / float(self.ball.max_hp) if self.ball.max_hp > 0 else 0.0

        # Fear: HP < 30%
        if hp_percent < 0.3:
            return "fear"

        # Bloodlust: Killed 2+ enemies
        kills = getattr(self.ball, "kills", 0)
        if kills >= 2:
            return "bloodlust"

        # Heroism: Any ally < 30% HP
        for ally in perception_data.get("allies", []):
            ally_hp_percent = 1.0
            if hasattr(ally, "get_hp_percent"):
                ally_hp_percent = ally.get_hp_percent()
            elif hasattr(ally, "hp") and hasattr(ally, "max_hp"):
                ally_hp_percent = float(ally.hp) / float(ally.max_hp) if ally.max_hp > 0 else 0.0
            if ally_hp_percent < 0.3:
                return "heroism"

        # Greed: Sees booster
        if len(perception_data.get("boosters", [])) > 0:
            return "greed"

        # Rage: HP > 80% and enemies present (simplified 'ally killed')
        if hp_percent > 0.8 and len(perception_data.get("enemies", [])) > 0:
            return "rage"

        # Cowardice: First hit (simplified: HP < 100% and just hit)
        if hp_percent < 1.0 and getattr(self.ball, "just_hit", False):
            # In a full implementation, we might reset `just_hit` here or in the ball's logic.
            return "cowardice"

        return "neutral"
