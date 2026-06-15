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
var current_strategy = "idle"

func _init(ball_ref, world_ref):
    self.ball = ball_ref
    self.world = world_ref
    self.perception_layer = Perception.new(self.ball, self.world)
    self.emotion_layer = EmotionLayer.new(self.ball, self.world)
    self.decision_layer = DecisionLayer.new(self.ball, self.world)
    self.action_layer = ActionLayer.new(self.ball, self.world)

# Main processing loop
func process(delta):
    var difficulty = "hard"
    if "difficulty" in self.ball:
        difficulty = self.ball.difficulty

    var delays = {
        "easy": 0.5,
        "medium": 0.2,
        "hard": 0.05,
        "chaos": 0.0
    }
    var reaction_delay = 0.05
    if delays.has(difficulty):
        reaction_delay = delays[difficulty]

    self.reaction_timer -= delta

    if self.reaction_timer <= 0 or difficulty == "chaos":
        var perception_data = perception()
        var emotion_state = emotion(perception_data)
        self.current_strategy = decision(perception_data, emotion_state)
        self.reaction_timer = reaction_delay

    action(self.current_strategy, delta)

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
