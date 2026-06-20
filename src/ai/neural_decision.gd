class_name NeuralDecision
extends RefCounted

var ball = null
var world = null

func _init(ball_ref, world_ref):
    self.ball = ball_ref
    self.world = world_ref

func choose_action(perception_data: Dictionary, emotion_state: String) -> String:
    var hp_percent = 1.0
    if self.ball.has_method("get_hp_percent"):
        hp_percent = self.ball.get_hp_percent()
    elif "hp" in self.ball and "max_hp" in self.ball and float(self.ball.max_hp) > 0:
        hp_percent = float(self.ball.hp) / float(self.ball.max_hp)

    var danger_level = 0.0
    if perception_data.has("danger_level"):
        danger_level = perception_data["danger_level"]

    var opportunity_score = 0.0
    if perception_data.has("opportunity_score"):
        opportunity_score = perception_data["opportunity_score"]

    var threat_level = 0.0
    if perception_data.has("threat_level"):
        threat_level = perception_data["threat_level"]

    var inputs = [hp_percent, danger_level, opportunity_score, threat_level]

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

    var actions = ["flee", "defend", "collect_booster", "attack", "chase", "use_skill", "kite", "flank", "group_attack", "hide_behind"]
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
