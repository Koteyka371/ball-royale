class_name NeuralNetworkBrain
extends BallBrain

const NeuralDecision = preload("res://src/ai/neural_decision.gd")

func _init(ball_ref, world_ref):
    super(ball_ref, world_ref)
    # Override decision layer with NeuralDecision
    self.decision_layer = NeuralDecision.new(self.ball, self.world)

func decision(perception_data: Dictionary, emotion_state: String) -> String:
    return self.decision_layer.choose_action(perception_data, emotion_state)
