class_name NeuralNetwork
extends RefCounted

var input_size: int
var hidden_size: int
var output_size: int

var weights_ih: Array = []
var bias_h: Array = []
var weights_ho: Array = []
var bias_o: Array = []

func _init(i_size: int, h_size: int, o_size: int, weights_data: Dictionary = {}):
    self.input_size = i_size
    self.hidden_size = h_size
    self.output_size = o_size

    if weights_data.has("weights_ih"):
        self.weights_ih = weights_data["weights_ih"]
        self.bias_h = weights_data["bias_h"]
        self.weights_ho = weights_data["weights_ho"]
        self.bias_o = weights_data["bias_o"]
    else:
        var rng = RandomNumberGenerator.new()
        rng.randomize()

        self.weights_ih = []
        for i in range(self.hidden_size):
            var row = []
            for j in range(self.input_size):
                row.append(rng.randf_range(-1.0, 1.0))
            self.weights_ih.append(row)

        self.bias_h = []
        for i in range(self.hidden_size):
            self.bias_h.append(rng.randf_range(-1.0, 1.0))

        self.weights_ho = []
        for i in range(self.output_size):
            var row = []
            for j in range(self.hidden_size):
                row.append(rng.randf_range(-1.0, 1.0))
            self.weights_ho.append(row)

        self.bias_o = []
        for i in range(self.output_size):
            self.bias_o.append(rng.randf_range(-1.0, 1.0))

func relu(x: float) -> float:
    return max(0.0, x)

func feedforward(inputs: Array) -> Array:
    var hidden = []
    for i in range(self.hidden_size):
        var sum_val = self.bias_h[i]
        for j in range(self.input_size):
            sum_val += inputs[j] * self.weights_ih[i][j]
        hidden.append(self.relu(sum_val))

    var outputs = []
    for i in range(self.output_size):
        var sum_val = self.bias_o[i]
        for j in range(self.hidden_size):
            sum_val += hidden[j] * self.weights_ho[i][j]
        outputs.append(sum_val)

    return outputs

func get_weights() -> Dictionary:
    return {
        "weights_ih": self.weights_ih,
        "bias_h": self.bias_h,
        "weights_ho": self.weights_ho,
        "bias_o": self.bias_o
    }
