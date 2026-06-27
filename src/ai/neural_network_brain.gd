class_name NeuralNetworkBrain
extends BallBrain

const NeuralDecision = preload("res://src/ai/neural_decision.gd")

func _init(ball_ref, world_ref):
    super(ball_ref, world_ref)
    # Override decision layer with NeuralDecision
    self.decision_layer = NeuralDecision.new(self.ball, self.world)

    var file = FileAccess.open("res://src/ui/neural_config.json", FileAccess.READ)
    if file != null:
        var text = file.get_as_text()
        file.close()
        var json = JSON.new()
        var error = json.parse(text)
        if error == OK:
            var data = json.get_data()
            if typeof(data) == TYPE_DICTIONARY and data.has("neural_inputs"):
                if "input_size" in self.ball:
                    self.ball.input_size = data["neural_inputs"].size()

func decision(perception_data: Dictionary, emotion_state: String) -> String:
    return self.decision_layer.choose_action(perception_data, emotion_state)
