from typing import Any, Dict

class Emotion:
    """
    Emotion system that models the ball's emotional state based on game design specs.
    States: Fear (low HP), Rage (ally killed/high HP sees enemies), Greed (sees booster),
            Cowardice (first hit), Heroism (ally in danger), Bloodlust (killed 2+ enemies).
    Emotions modify behavior.
    """

    def __init__(self, ball: Any, world: Any):
        self.ball = ball
        self.world = world
        self.has_taken_first_hit_previously = False # track if we already reacted to first hit

    def get_state(self, perception_data: Dict[str, Any]) -> str:
        """
        Determines current emotional state based on ball state and perception.
        Priority: Fear -> Cowardice -> Heroism -> Bloodlust -> Greed -> Rage -> Neutral
        (Can adjust priority if needed, but this order ensures life-saving emotions come first)
        """
        hp_percent = 1.0
        if hasattr(self.ball, "get_hp_percent"):
            hp_percent = self.ball.get_hp_percent()
        elif hasattr(self.ball, "hp") and hasattr(self.ball, "max_hp"):
            hp_percent = float(self.ball.hp) / float(self.ball.max_hp)

        # 1. Fear: HP < 30%
        if hp_percent < 0.3:
            return "fear"

        # 2. Cowardice: first hit (if first_hit_taken is True and we haven't reacted yet)
        if getattr(self.ball, "first_hit_taken", False) and not self.has_taken_first_hit_previously:
            # Once we've experienced Cowardice, we remember it so we don't stay Cowardice forever
            self.has_taken_first_hit_previously = True
            return "cowardice"

        # 3. Heroism: ally < 30% HP
        allies = perception_data.get("allies", [])
        for ally in allies:
            ally_hp_percent = 1.0
            if hasattr(ally, "get_hp_percent"):
                ally_hp_percent = ally.get_hp_percent()
            elif hasattr(ally, "hp") and hasattr(ally, "max_hp"):
                ally_hp_percent = float(ally.hp) / float(ally.max_hp)
            if ally_hp_percent < 0.3:
                return "heroism"

        # 4. Bloodlust: killed 2+ enemies
        kills = getattr(self.ball, "kills", 0)
        if kills >= 2:
            return "bloodlust"

        # 5. Greed: sees booster
        if len(perception_data.get("boosters", [])) > 0:
            return "greed"

        # 6. Rage: HP > 80% and sees enemy (game design also says "ally killed",
        # but tracking ally death is tricky without world events. Just doing HP > 80% and enemies > 0)
        if hp_percent > 0.8 and len(perception_data.get("enemies", [])) > 0:
            return "rage"

        return "neutral"
