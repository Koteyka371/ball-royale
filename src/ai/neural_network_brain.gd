class_name NeuralNetworkBrain
extends RefCounted

var nn: NeuralNetwork
const ACTIONS = ["flee", "defend", "collect_booster", "attack", "chase", "use_skill"]

func _init(nn_weights: Dictionary = {}):
    # 4 inputs, 8 hidden nodes, 6 outputs
    self.nn = NeuralNetwork.new(4, 8, 6, nn_weights)

func evaluate(hp_percent: float, danger_level: float, opportunity_score: float, threat_level: float) -> String:
    var inputs = [hp_percent, danger_level, opportunity_score, threat_level]
    var outputs = self.nn.feedforward(inputs)

    var best_score = -999999.0
    var best_action_index = 0

    for i in range(outputs.size()):
        if outputs[i] > best_score:
            best_score = outputs[i]
            best_action_index = i

    return self.ACTIONS[best_action_index]
