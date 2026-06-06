class_name Emotion
extends RefCounted

var ball = null
var world = null

func _init(ball_ref, world_ref = null):
    self.ball = ball_ref
    self.world = world_ref

func process(perception_data: Dictionary) -> String:
    var hp_percent = 1.0
    if self.ball.has_method("get_hp_percent"):
        hp_percent = self.ball.get_hp_percent()
    elif "hp" in self.ball and "max_hp" in self.ball:
        hp_percent = float(self.ball.hp) / float(self.ball.max_hp)

    # Bloodlust (killed 2+ enemies)
    var kills = 0
    if "kills" in self.ball:
        kills = self.ball.kills
    if kills >= 2:
        return "bloodlust"

    # Fear (low HP)
    if hp_percent < 0.3:
        return "fear"

    # Cowardice (first hit)
    var has_taken_damage = false
    if "has_taken_damage" in self.ball:
        has_taken_damage = self.ball.has_taken_damage
    if has_taken_damage and hp_percent > 0.8:
        return "cowardice"

    # Rage (ally killed)
    var ally_killed = false
    if "ally_killed_recently" in self.ball:
        ally_killed = self.ball.ally_killed_recently
    if ally_killed:
        return "rage"

    # Heroism (ally in danger)
    var allies = []
    if perception_data.has("allies"):
        allies = perception_data["allies"]

    for ally in allies:
        var ally_hp_percent = 1.0
        if ally.has_method("get_hp_percent"):
            ally_hp_percent = ally.get_hp_percent()
        elif "hp" in ally and "max_hp" in ally:
            ally_hp_percent = float(ally.hp) / float(ally.max_hp)

        if ally_hp_percent < 0.3:
            return "heroism"

    # Greed (sees booster)
    if perception_data.has("boosters") and perception_data["boosters"].size() > 0:
        return "greed"

    return "neutral"
