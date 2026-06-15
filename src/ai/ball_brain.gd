class_name BallBrain
extends Node

const Perception = preload("res://src/ai/perception.gd")
const EmotionLayer = preload("res://src/ai/emotion.gd")
const DecisionLayer = preload("res://src/ai/decision.gd")
const ActionLayer = preload("res://src/ai/action.gd")
const NeuralNetworkCls = preload("res://src/ai/neural_network.gd")

const ACTIONS = ["flee", "defend", "collect_booster", "attack", "chase", "use_skill", "idle"]

# Reference to the ball this brain controls
var ball = null
var world = null
var perception_layer = null
var emotion_layer = null
var decision_layer = null
var action_layer = null

var is_neural = false
var nn = null
var last_hp = 100
var last_kills = 0

func _init(ball_ref, world_ref):
    self.ball = ball_ref
    self.world = world_ref
    self.perception_layer = Perception.new(self.ball, self.world)
    self.emotion_layer = EmotionLayer.new(self.ball, self.world)
    self.decision_layer = DecisionLayer.new(self.ball, self.world)
    self.action_layer = ActionLayer.new(self.ball, self.world)

    if "ball_type" in self.ball and self.ball.ball_type == "neural":
        self.is_neural = true
        self.nn = NeuralNetworkCls.new(5, 8, 7)
        if self.ball.has_meta("nn_weights"):
            self.nn.set_weights(self.ball.get_meta("nn_weights"))
        else:
            if self.nn.load("res://src/ai/nn_weights.json") or self.nn.load("src/ai/nn_weights.json"):
                self.ball.set_meta("nn_weights", self.nn.get_weights())

        if "hp" in self.ball:
            self.last_hp = self.ball.hp
        if "kills" in self.ball:
            self.last_kills = self.ball.kills

# Main processing loop
func process(delta):
    var perception_data = perception()
    var emotion_state = emotion(perception_data)
    var decision = decision(perception_data, emotion_state)

    if self.is_neural:
        var current_hp = self.last_hp
        var current_kills = self.last_kills

        if "hp" in self.ball:
            current_hp = self.ball.hp
        if "kills" in self.ball:
            current_kills = self.ball.kills

        var reward = 0.0
        if current_kills > self.last_kills:
            reward += 10.0
        if current_hp < self.last_hp:
            reward -= 1.0

        if reward != 0.0:
            var action_idx = ACTIONS.find(decision)
            if action_idx == -1:
                action_idx = 6 # idle
            self.nn.reinforce(action_idx, reward, 0.05)

        self.last_hp = current_hp
        self.last_kills = current_kills

    action(decision, delta)

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
    if self.is_neural:
        var hp_percent = 1.0
        if self.ball.has_method("get_hp_percent"):
            hp_percent = self.ball.get_hp_percent()
        elif "hp" in self.ball and "max_hp" in self.ball:
            hp_percent = float(self.ball.hp) / float(self.ball.max_hp)

        var danger_level = 0.0
        if perception_data.has("danger_level"):
            danger_level = perception_data["danger_level"]

        var threat_level = 0.0
        if perception_data.has("threat_level"):
            threat_level = perception_data["threat_level"]

        var opportunity_score = 0.0
        if perception_data.has("opportunity_score"):
            opportunity_score = perception_data["opportunity_score"]

        var has_enemies = 0.0
        if perception_data.has("enemies") and perception_data["enemies"].size() > 0:
            has_enemies = 1.0

        var inputs = [
            hp_percent,
            danger_level,
            threat_level,
            opportunity_score,
            has_enemies
        ]

        var outputs = self.nn.predict(inputs)

        var best_action_idx = 0
        var best_activation = -1.0

        for i in range(outputs.size()):
            if outputs[i] > best_activation:
                best_activation = outputs[i]
                best_action_idx = i

        return ACTIONS[best_action_idx]

    return self.decision_layer.choose_action(perception_data, emotion_state)

# 4. ACTION LAYER
# Delegates executing chosen strategy to the ActionLayer
func action(strategy: String, delta: float):
    self.action_layer.execute(strategy, delta)
