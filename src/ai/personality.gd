class_name Personality
extends RefCounted

# Defines the ball's character and provides decision modifiers.
# Supported characters: aggressive, cautious, supportive, reckless, cunning

var character: String = "idle"
var original_type: String = ""

func _init(char_type: String = "idle", orig_type: String = ""):
    self.character = char_type
    self.original_type = orig_type if orig_type != "" else char_type

func get_decision_modifiers() -> Dictionary:
    var modifiers = {
        "flee": 0.0,
        "defend": 0.0,
        "opportunistic": 0.0,
        "attack": 0.0,
        "chase": 0.0,
        "use_skill": 0.0,
        "idle": 0.0
    }

    if self.character == "aggressive":
        modifiers["attack"] += 20.0
        modifiers["chase"] += 20.0
        modifiers["flee"] -= 20.0
    elif self.character == "cautious":
        modifiers["flee"] += 20.0
        modifiers["defend"] += 20.0
        modifiers["attack"] -= 10.0
        modifiers["chase"] -= 20.0
    elif self.character == "supportive":
        modifiers["defend"] += 30.0
        modifiers["use_skill"] += 10.0
    elif self.character == "reckless":
        modifiers["attack"] += 30.0
        modifiers["use_skill"] += 20.0
        modifiers["flee"] -= 50.0
        modifiers["defend"] -= 20.0
    elif self.character == "cunning":
        modifiers["opportunistic"] += 20.0
        modifiers["chase"] += 10.0
        modifiers["defend"] += 10.0

    return modifiers

func _to_string():
    return self.character
