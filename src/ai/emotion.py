from typing import Any, Dict

class Emotion:
    """
    Emotion system that determines the ball's current emotional state.
    Emotions modify behavior in the decision layer.
    """

    def __init__(self, ball: Any, world: Any = None):
        self.ball = ball
        self.world = world

    def process(self, perception_data: Dict[str, Any]) -> str:
        """
        Processes perception data and internal ball state to determine emotion.
        Returns the dominant emotion as a string.
        """
        # Get HP percent
        hp_percent = 1.0
        if hasattr(self.ball, "get_hp_percent"):
            hp_percent = self.ball.get_hp_percent()
        elif hasattr(self.ball, "hp") and hasattr(self.ball, "max_hp"):
            hp_percent = float(self.ball.hp) / float(self.ball.max_hp)

        # Bloodlust (killed 2+ enemies)
        kills = getattr(self.ball, "kills", 0)
        if kills >= 2:
            return "bloodlust"

        # Fear (low HP)
        if hp_percent < 0.3:
            return "fear"

        # Cowardice (first hit)
        has_taken_damage = getattr(self.ball, "has_taken_damage", False)
        # Assuming if hp < max_hp and it just happened recently, or we could just use has_taken_damage and low courage.
        # We'll just define Cowardice as: taking damage for the first time while HP is high
        if has_taken_damage and hp_percent > 0.8:
            return "cowardice"

        # Rage (ally killed)
        ally_killed = getattr(self.ball, "ally_killed_recently", False)
        if ally_killed:
            return "rage"

        # Heroism (ally in danger)
        allies = perception_data.get("allies", [])
        for ally in allies:
            ally_hp_percent = 1.0
            if hasattr(ally, "get_hp_percent"):
                ally_hp_percent = ally.get_hp_percent()
            elif hasattr(ally, "hp") and hasattr(ally, "max_hp"):
                ally_hp_percent = float(ally.hp) / float(ally.max_hp)

            if ally_hp_percent < 0.3:
                return "heroism"

        # Greed (sees booster)
        if len(perception_data.get("boosters", [])) > 0:
            return "greed"

        return "neutral"
