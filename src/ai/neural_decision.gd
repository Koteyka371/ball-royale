class_name NeuralDecision
extends RefCounted

var ball = null
var world = null

var configured_inputs = ["hp_percent", "danger_level", "opportunity_score", "threat_level", "distance_to_zone"]

func _init(ball_ref, world_ref):
    self.ball = ball_ref
    self.world = world_ref

    var file = FileAccess.open("res://src/ui/neural_config.json", FileAccess.READ)
    if file != null:
        var text = file.get_as_text()
        file.close()
        var json = JSON.new()
        var error = json.parse(text)
        if error == OK:
            var data = json.get_data()
            if typeof(data) == TYPE_DICTIONARY and data.has("neural_inputs"):
                self.configured_inputs = data["neural_inputs"]

func choose_action(perception_data: Dictionary, emotion_state: String) -> String:
    var inputs = []
    for input_name in self.configured_inputs:
        if input_name == "hp_percent":
            var hp_percent = 1.0
            if self.ball.has_method("get_hp_percent"):
                hp_percent = self.ball.get_hp_percent()
            elif "hp" in self.ball and "max_hp" in self.ball and float(self.ball.max_hp) > 0:
                hp_percent = float(self.ball.hp) / float(self.ball.max_hp)
            inputs.append(hp_percent)
        elif input_name == "danger_level":
            var danger_level = 0.0
            if perception_data.has("danger_level"):
                danger_level = float(perception_data["danger_level"])
            inputs.append(danger_level)
        elif input_name == "opportunity_score":
            var opportunity_score = 0.0
            if perception_data.has("opportunity_score"):
                opportunity_score = float(perception_data["opportunity_score"])
            inputs.append(opportunity_score)
        elif input_name == "threat_level":
            var threat_level = 0.0
            if perception_data.has("threat_level"):
                threat_level = float(perception_data["threat_level"])
            inputs.append(threat_level)
        elif input_name == "nearest_enemy_distance":
            var val = 1000.0
            if perception_data.has("enemies") and "x" in self.ball and "y" in self.ball:
                for e in perception_data["enemies"]:
                    if "x" in e and "y" in e:
                        var d = sqrt(pow(e.x - self.ball.x, 2) + pow(e.y - self.ball.y, 2))
                        if d < val:
                            val = d
            inputs.append(val)
        elif input_name == "distance_to_zone":
            var distance_to_zone = 1000.0
            if self.world != null and "game_mode" in self.world and self.world.game_mode != null:
                var gm = self.world.game_mode
                if "name" in gm and gm.name == "Moving Zone":
                    var zone_x = 500.0
                    var zone_y = 500.0
                    if "zone_x" in gm: zone_x = float(gm.zone_x)
                    if "zone_y" in gm: zone_y = float(gm.zone_y)
                    if "x" in self.ball and "y" in self.ball:
                        var dx = self.ball.x - zone_x
                        var dy = self.ball.y - zone_y
                        distance_to_zone = sqrt(dx * dx + dy * dy)
            inputs.append(distance_to_zone)
        elif input_name == "number_of_allies":
            var val = 0.0
            if perception_data.has("allies"):
                val = float(perception_data["allies"].size())
            inputs.append(val)
        elif input_name == "boss_hp":
            var val = 0.0
            if perception_data.has("enemies"):
                for e in perception_data["enemies"]:
                    if "ball_type" in e and e.ball_type == "juggernaut" and "hp" in e:
                        val = float(e.hp)
                        break
            inputs.append(val)
        elif input_name == "map_hazard_distance":
            var val = 1000.0
            if perception_data.has("traps") and "x" in self.ball and "y" in self.ball:
                for t in perception_data["traps"]:
                    if "x" in t and "y" in t:
                        var d = sqrt(pow(t.x - self.ball.x, 2) + pow(t.y - self.ball.y, 2))
                        if d < val:
                            val = d
            inputs.append(val)
        elif input_name == "skill_dash":
            inputs.append(1.0 if ("SKILL" in self.ball and self.ball.SKILL == "dash") else 0.0)
        elif input_name == "skill_shield":
            inputs.append(1.0 if ("SKILL" in self.ball and self.ball.SKILL == "shield") else 0.0)
        elif input_name == "skill_heal":
            inputs.append(1.0 if ("SKILL" in self.ball and self.ball.SKILL == "heal") else 0.0)
        else:
            inputs.append(0.0)

    var weights = null
    var biases = null

    if "nn_weights" in self.ball:
        weights = self.ball.nn_weights
    elif self.ball.has_meta("nn_weights"):
        weights = self.ball.get_meta("nn_weights")

    if "nn_biases" in self.ball:
        biases = self.ball.nn_biases
    elif self.ball.has_meta("nn_biases"):
        biases = self.ball.get_meta("nn_biases")

    if weights == null or biases == null:
        var file = FileAccess.open("res://src/ai/nn_weights.json", FileAccess.READ)
        if file != null:
            var content = file.get_as_text()
            file.close()
            var json = JSON.new()
            var error = json.parse(content)
            if error == OK:
                var data = json.get_data()
                if data.has("weights") and data.has("biases"):
                    weights = data["weights"]
                    biases = data["biases"]
                    if self.ball.has_method("set_meta"):
                        self.ball.set_meta("nn_weights", weights)
                        self.ball.set_meta("nn_biases", biases)

    if weights == null or biases == null:
        return "idle"

    var actions = ["flee", "defend", "collect_booster", "attack", "chase", "use_skill", "kite", "flank", "group_attack", "hide_behind", "hold_zone"]
    var best_score = -9999.0
    var best_action = "idle"

    for i in range(actions.size()):
        if i < biases.size():
            var score = biases[i]
            for j in range(inputs.size()):
                if i < weights.size() and j < weights[i].size():
                    score += inputs[j] * weights[i][j]
            if score > best_score:
                best_score = score
                best_action = actions[i]

    var skill_timer = 0.0
    if "skill_timer" in self.ball:
        skill_timer = self.ball.skill_timer
    if best_action == "use_skill" and skill_timer > 0:
        return "chase"

    return best_action
