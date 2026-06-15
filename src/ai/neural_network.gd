class_name NeuralNetwork
extends RefCounted

var input_size: int
var hidden_size: int
var output_size: int

var weights_ih: Array = []
var bias_h: Array = []
var weights_ho: Array = []
var bias_o: Array = []

var last_inputs: Array = []
var last_hidden: Array = []

func _init(i_size: int, h_size: int, o_size: int):
    self.input_size = i_size
    self.hidden_size = h_size
    self.output_size = o_size

    # Initialize randomly between -1 and 1
    randomize()

    weights_ih = []
    for i in range(hidden_size):
        var row = []
        for j in range(input_size):
            row.append(randf_range(-1.0, 1.0))
        weights_ih.append(row)

    bias_h = []
    for i in range(hidden_size):
        bias_h.append(randf_range(-1.0, 1.0))

    weights_ho = []
    for i in range(output_size):
        var row = []
        for j in range(hidden_size):
            row.append(randf_range(-1.0, 1.0))
        weights_ho.append(row)

    bias_o = []
    for i in range(output_size):
        bias_o.append(randf_range(-1.0, 1.0))

func _sigmoid(x: float) -> float:
    var cx = max(min(x, 20.0), -20.0)
    return 1.0 / (1.0 + exp(-cx))

func _relu(x: float) -> float:
    return max(0.0, x)

func predict(inputs: Array) -> Array:
    if inputs.size() != input_size:
        push_error("Expected " + str(input_size) + " inputs, got " + str(inputs.size()))
        return []

    last_inputs = inputs.duplicate()

    # Input to Hidden
    var hidden = []
    for i in range(hidden_size):
        var sum_val = bias_h[i]
        for j in range(input_size):
            sum_val += inputs[j] * weights_ih[i][j]
        hidden.append(_relu(sum_val))

    last_hidden = hidden.duplicate()

    # Hidden to Output
    var outputs = []
    for i in range(output_size):
        var sum_val = bias_o[i]
        for j in range(hidden_size):
            sum_val += hidden[j] * weights_ho[i][j]
        outputs.append(_sigmoid(sum_val))

    return outputs

func get_weights() -> Dictionary:
    return {
        "input_size": input_size,
        "hidden_size": hidden_size,
        "output_size": output_size,
        "weights_ih": weights_ih.duplicate(true),
        "bias_h": bias_h.duplicate(true),
        "weights_ho": weights_ho.duplicate(true),
        "bias_o": bias_o.duplicate(true)
    }

func set_weights(weights: Dictionary):
    if weights["input_size"] != input_size or weights["hidden_size"] != hidden_size or weights["output_size"] != output_size:
        input_size = weights["input_size"]
        hidden_size = weights["hidden_size"]
        output_size = weights["output_size"]

    weights_ih = weights["weights_ih"].duplicate(true)
    bias_h = weights["bias_h"].duplicate(true)
    weights_ho = weights["weights_ho"].duplicate(true)
    bias_o = weights["bias_o"].duplicate(true)

func save(filepath: String):
    var file = FileAccess.open(filepath, FileAccess.WRITE)
    if file:
        file.store_string(JSON.stringify(get_weights(), "\t"))
        file.close()

func load(filepath: String) -> bool:
    if not FileAccess.file_exists(filepath):
        return false

    var file = FileAccess.open(filepath, FileAccess.READ)
    if not file:
        return false

    var content = file.get_as_text()
    file.close()

    var json = JSON.new()
    var error = json.parse(content)
    if error == OK:
        set_weights(json.data)
        return true
    return false

func mutate(rate: float):
    var rand_gauss = func():
        var u1 = randf()
        var u2 = randf()
        return sqrt(-2.0 * log(u1)) * cos(2.0 * PI * u2)

    for i in range(hidden_size):
        for j in range(input_size):
            if randf() < rate:
                weights_ih[i][j] += rand_gauss.call() * 0.1
        if randf() < rate:
            bias_h[i] += rand_gauss.call() * 0.1

    for i in range(output_size):
        for j in range(hidden_size):
            if randf() < rate:
                weights_ho[i][j] += rand_gauss.call() * 0.1
        if randf() < rate:
            bias_o[i] += rand_gauss.call() * 0.1

func reinforce(action_index: int, reward: float, learning_rate: float = 0.01):
    if last_inputs.size() == 0 or last_hidden.size() == 0:
        return

    # Nudge weights from hidden to output
    for j in range(hidden_size):
        var delta = learning_rate * reward * last_hidden[j]
        weights_ho[action_index][j] += delta

    # Nudge bias for specific action
    bias_o[action_index] += learning_rate * reward

    # Nudge weights from input to hidden based on contribution
    for i in range(hidden_size):
        var ho_weight = weights_ho[action_index][i]
        for j in range(input_size):
            var delta = learning_rate * reward * ho_weight * last_inputs[j]
            weights_ih[i][j] += delta

        bias_h[i] += learning_rate * reward * ho_weight
