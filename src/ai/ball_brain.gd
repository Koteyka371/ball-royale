class_name BallBrain
extends Node

const Perception = preload("res://src/ai/perception.gd")
const EmotionLayer = preload("res://src/ai/emotion.gd")
const DecisionLayer = preload("res://src/ai/decision.gd")

# Reference to the ball this brain controls
var ball = null
var world = null
var perception_layer = null
var emotion_layer = null
var decision_layer = null

func _init(ball_ref, world_ref):
    self.ball = ball_ref
    self.world = world_ref
    self.perception_layer = Perception.new(self.ball, self.world)
    self.emotion_layer = EmotionLayer.new(self.ball, self.world)
    self.decision_layer = DecisionLayer.new(self.ball, self.world)

# Main processing loop
func process(delta):
    var perception_data = perception()
    var emotion_state = emotion(perception_data)
    var decision = decision(perception_data, emotion_state)
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
    return self.decision_layer.choose_action(perception_data, emotion_state)

# 4. ACTION LAYER
# Executes chosen strategy
func action(strategy: String, delta: float):
    # Depending on strategy, call the appropriate behavior on the ball
    if strategy == "flee":
        if self.ball.has_method("flee"):
            self.ball.flee(delta)
    elif strategy == "attack":
        if self.ball.has_method("attack"):
            self.ball.attack(delta)
    elif strategy == "defend":
        if self.ball.has_method("defend"):
            self.ball.defend(delta)
    elif strategy == "opportunistic":
        if self.ball.has_method("collect_booster"):
            self.ball.collect_booster(delta)
    else:
        if self.ball.has_method("idle"):
            self.ball.idle(delta)
