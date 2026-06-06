class_name Emotion
extends RefCounted

var ball = null

func _init(ball_ref):
    self.ball = ball_ref

func process(perception_data: Dictionary) -> String:
    var hp_percent = 1.0
    if self.ball.has_method("get_hp_percent"):
        hp_percent = self.ball.get_hp_percent()
    elif "hp" in self.ball and "max_hp" in self.ball:
        if self.ball.max_hp > 0:
            hp_percent = float(self.ball.hp) / float(self.ball.max_hp)
        else:
            hp_percent = 0.0

    # Fear: HP < 30%
    if hp_percent < 0.3:
        return "fear"

    # Bloodlust: Killed 2+ enemies
    var kills = 0
    if "kills" in self.ball:
        kills = self.ball.kills
    if kills >= 2:
        return "bloodlust"

    # Heroism: Any ally < 30% HP
    for ally in perception_data.get("allies", []):
        var ally_hp_percent = 1.0
        if ally.has_method("get_hp_percent"):
            ally_hp_percent = ally.get_hp_percent()
        elif "hp" in ally and "max_hp" in ally:
            if ally.max_hp > 0:
                ally_hp_percent = float(ally.hp) / float(ally.max_hp)
            else:
                ally_hp_percent = 0.0
        if ally_hp_percent < 0.3:
            return "heroism"

    # Greed: Sees booster
    if perception_data.get("boosters", []).size() > 0:
        return "greed"

    # Rage: HP > 80% and enemies present
    if hp_percent > 0.8 and perception_data.get("enemies", []).size() > 0:
        return "rage"

    # Cowardice: First hit
    var just_hit = false
    if "just_hit" in self.ball:
        just_hit = self.ball.just_hit
    if hp_percent < 1.0 and just_hit:
        return "cowardice"

    return "neutral"
