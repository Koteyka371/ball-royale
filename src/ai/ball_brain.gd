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
var reaction_timer = 0.0
var last_decision = "idle"

func _init(ball_ref, world_ref):
    self.ball = ball_ref
    self.world = world_ref
    self.perception_layer = Perception.new(self.ball, self.world)
    self.emotion_layer = EmotionLayer.new(self.ball, self.world)
    self.decision_layer = DecisionLayer.new(self.ball, self.world)
    self.action_layer = ActionLayer.new(self.ball, self.world)
    self.reaction_timer = 0.0
    self.last_decision = "idle"

# Main processing loop
func process(delta):
    self.reaction_timer -= delta
    var difficulty = "medium"
    if "difficulty" in self.ball:
        difficulty = self.ball.difficulty

    if self.reaction_timer <= 0:
        var perception_data = perception()
        var emotion_state = emotion(perception_data)
        self.last_decision = decision(perception_data, emotion_state)

        if difficulty == "easy":
            self.reaction_timer = 0.5
        elif difficulty == "medium":
            self.reaction_timer = 0.1
        elif difficulty == "hard":
            self.reaction_timer = 0.0
        elif difficulty == "chaos":
            self.reaction_timer = randf_range(0.0, 0.5)
        else:
            self.reaction_timer = 0.1

    action(self.last_decision, delta)

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
