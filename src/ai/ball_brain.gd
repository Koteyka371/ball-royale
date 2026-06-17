class_name BallBrain
extends Node

const Perception = preload("res://src/ai/perception.gd")
const EmotionLayer = preload("res://src/ai/emotion.gd")
const DecisionLayer = preload("res://src/ai/decision.gd")
const ActionLayer = preload("res://src/ai/action.gd")

# Reference to the ball this brain controls
var ball = null
var world = null
var perception_layer = null
var emotion_layer = null
var decision_layer = null
var action_layer = null

var _reaction_timer = 0.0
var _current_decision = "idle"

func _init(ball_ref, world_ref):
    self.ball = ball_ref
    self.world = world_ref
    self.perception_layer = Perception.new(self.ball, self.world)
    self.emotion_layer = EmotionLayer.new(self.ball, self.world)
    self.decision_layer = DecisionLayer.new(self.ball, self.world)
    self.action_layer = ActionLayer.new(self.ball, self.world)

# Main processing loop
func process(delta):
    self._reaction_timer -= delta

    if self._reaction_timer <= 0:
        var perception_data = perception()
        var emotion_state = emotion(perception_data)

        var b_type = ""
        if "ball_type" in self.ball:
            b_type = self.ball.ball_type.to_lower()
        elif self.ball.has_method("get_ball_type"):
            b_type = self.ball.get_ball_type().to_lower()

        var override_disabled = false
        if OS.has_environment("DISABLE_NN_OVERRIDE"):
            override_disabled = true

        var decision_str = ""
        if b_type == "neural" and not override_disabled:
            decision_str = _neural_decision(perception_data)
        else:
            decision_str = decision(perception_data, emotion_state)

        self._current_decision = decision_str

        var difficulty = "medium"
        if "difficulty" in self.ball:
            difficulty = self.ball.difficulty

        if difficulty == "easy":
            self._reaction_timer = 0.5
        elif difficulty == "medium":
            self._reaction_timer = 0.1
        elif difficulty == "hard":
            self._reaction_timer = 0.0
        elif difficulty == "chaos":
            self._reaction_timer = randf_range(0.0, 0.2)
        else:
            self._reaction_timer = 0.1

    action(self._current_decision, delta)

# 1. PERCEPTION LAYER
# Scans environment for entities via Perception layer
func perception() -> Dictionary:
    return self.perception_layer.scan()

# 2. EMOTION LAYER
# Delegates determining current emotional state to the Emotion class.
func emotion(perception_data: Dictionary) -> String:
    return self.emotion_layer.get_state(perception_data)

# 3. DECISION LAYER
# Chooses strategy based on perception and emotion
func decision(perception_data: Dictionary, emotion_state: String) -> String:
    return self.decision_layer.choose_action(perception_data, emotion_state)

# 4. ACTION LAYER
# Delegates executing chosen strategy to the ActionLayer
func action(strategy: String, delta: float):
    self.action_layer.execute(strategy, delta)

func _neural_decision(perception_data: Dictionary) -> String:
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
        return decision(perception_data, emotion(perception_data))

    var actions = ["flee", "defend", "collect_booster", "attack", "chase", "use_skill"]
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
