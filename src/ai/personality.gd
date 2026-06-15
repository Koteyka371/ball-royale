class_name Personality
extends RefCounted

var character: String

func _init(char_type: String = "cautious"):
    self.character = char_type

func get_decision_modifiers() -> Dictionary:
    var modifiers = {
        "attack": 0.0,
        "flee": 0.0,
        "defend": 0.0,
        "chase": 0.0,
        "opportunistic": 0.0,
        "use_skill": 0.0
    }

    if character == "aggressive":
        modifiers["attack"] = 30.0
        modifiers["chase"] = 30.0
        modifiers["flee"] = -20.0
    elif character == "cautious":
        modifiers["defend"] = 30.0
        modifiers["flee"] = 20.0
        modifiers["attack"] = -10.0
        modifiers["chase"] = -10.0
    elif character == "supportive":
        modifiers["defend"] = 20.0
        modifiers["use_skill"] = 20.0
    elif character == "reckless":
        modifiers["attack"] = 40.0
        modifiers["chase"] = 40.0
        modifiers["flee"] = -50.0
        modifiers["defend"] = -20.0
    elif character == "cunning":
        modifiers["opportunistic"] = 40.0
        modifiers["flee"] = 10.0
        modifiers["attack"] = -10.0

    return modifiers

static func get_default_personality(ball_type: String) -> Personality:
    var mapping = {
        "assassin": "aggressive",
        "berserker": "reckless",
        "bomber": "reckless",
        "guardian": "cautious",
        "healer": "supportive",
        "juggernaut": "cautious",
        "phantom": "cunning",
        "rogue": "cunning",
        "sniper": "cautious",
        "swarm": "aggressive",
        "tank": "cautious",
        "warrior": "aggressive"
    }

    var char_type = "cautious"
    if mapping.has(ball_type):
        char_type = mapping[ball_type]

    return Personality.new(char_type)
