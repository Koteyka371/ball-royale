class_name Emotion
extends RefCounted

var ball = null
var world = null
var has_taken_first_hit_previously = false

func _init(ball_ref, world_ref):
    self.ball = ball_ref
    self.world = world_ref
    self.has_taken_first_hit_previously = false

func get_state(perception_data: Dictionary) -> String:
    var hp_percent = 1.0
    if self.ball.has_method("get_hp_percent"):
        hp_percent = self.ball.get_hp_percent()
    elif "hp" in self.ball and "max_hp" in self.ball:
        hp_percent = float(self.ball.hp) / float(self.ball.max_hp)

    # 1. Fear: HP < 30%
    if hp_percent < 0.3:
        return "fear"

    # 2. Cowardice: first hit
    var first_hit = false
    if "first_hit_taken" in self.ball:
        first_hit = self.ball.first_hit_taken

    if first_hit and not self.has_taken_first_hit_previously:
        self.has_taken_first_hit_previously = true
        return "cowardice"

    # 3. Heroism: ally < 30% HP or request_help
    var team_messages = []
    if perception_data.has("team_messages"):
        team_messages = perception_data["team_messages"]

    for msg in team_messages:
        if msg != null and msg.has("type") and msg.type == "request_help":
            return "heroism"

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

    # 4. Bloodlust: killed 2+ enemies
    var kills = 0
    if "kills" in self.ball:
        kills = self.ball.kills

    if kills >= 2:
        return "bloodlust"

    # 5. Greed: sees booster
    if perception_data.has("boosters") and perception_data["boosters"].size() > 0:
        return "greed"

    # 6. Rage: HP > 80% and sees enemy
    if hp_percent > 0.8 and perception_data.has("enemies") and perception_data["enemies"].size() > 0:
        return "rage"

    return "neutral"
