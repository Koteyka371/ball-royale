class_name Personality
extends RefCounted

var character: String = "idle"

func _init(char_name: String = "idle"):
    self.character = char_name

func get_decision_modifiers() -> Dictionary:
    var mods = {
        "flee": 0.0,
        "defend": 0.0,
        "opportunistic": 0.0,
        "attack": 0.0,
        "chase": 0.0,
        "use skill": 0.0,
        "idle": 0.0
    }

    if self.character == "aggressive":
        mods["attack"] += 20.0
        mods["chase"] += 15.0
        mods["flee"] -= 10.0
    elif self.character == "cautious":
        mods["flee"] += 20.0
        mods["defend"] += 15.0
        mods["chase"] -= 10.0
    elif self.character == "supportive":
        mods["defend"] += 20.0
        mods["attack"] -= 5.0
        mods["chase"] -= 5.0
    elif self.character == "reckless":
        mods["attack"] += 30.0
        mods["chase"] += 25.0
        mods["flee"] -= 50.0
        mods["defend"] -= 20.0
    elif self.character == "cunning":
        mods["opportunistic"] += 20.0
        mods["chase"] += 20.0
        mods["defend"] -= 10.0

    return mods
