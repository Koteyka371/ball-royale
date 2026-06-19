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

        if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"):
            self.ball.set_meta("emotion", emotion_state)
        elif "emotion" in self.ball:
            self.ball.emotion = emotion_state

        var decision_str = decision(perception_data, emotion_state)
        self._current_decision = decision_str

        var difficulty = "medium"
        if "difficulty" in self.ball:
            difficulty = self.ball.difficulty

        if difficulty == "easy":
            self._reaction_timer = 0.5
        elif difficulty == "medium":
            self._reaction_timer = 0.1
        elif difficulty == "hard":
            self._reaction_timer = 0.05
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
