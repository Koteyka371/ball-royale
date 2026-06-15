class_name DecisionLayer
extends RefCounted

# Decision system that evaluates options and chooses an action.
# Weighs threat level, opportunity, personality, emotional state.
# Returns best action: chase, flee, attack, use skill, collect booster, defend.

var ball = null
var world = null

func _init(ball_ref, world_ref):
    self.ball = ball_ref
    self.world = world_ref

func choose_action(perception_data: Dictionary, emotion_state: String) -> String:
    var hp_percent = 1.0
    if self.ball.has_method("get_hp_percent"):
        hp_percent = self.ball.get_hp_percent()
    elif "hp" in self.ball and "max_hp" in self.ball:
        hp_percent = float(self.ball.hp) / float(self.ball.max_hp)

    var scores = {
        "flee": 0.0,
        "defend": 0.0,
        "opportunistic": 0.0,
        "attack": 0.0,
        "idle": 0.0
    }

    var danger_level = 0.0
    if perception_data.has("danger_level"):
        danger_level = perception_data["danger_level"]

    var opportunity_level = 0.0
    if perception_data.has("opportunity_level"):
        opportunity_level = perception_data["opportunity_level"]

    var enemies = []
    if perception_data.has("enemies"):
        enemies = perception_data["enemies"]

    var boosters = []
    if perception_data.has("boosters"):
        boosters = perception_data["boosters"]

    var personality = "idle"
    if "personality" in self.ball:
        personality = self.ball.personality

    var team_messages = []
    if perception_data.has("team_messages"):
        team_messages = perception_data["team_messages"]

    # Process team messages
    for msg in team_messages:
        if typeof(msg) == TYPE_DICTIONARY and msg.has("type"):
            var msg_type = msg["type"]
            if msg_type == "hold_position":
                scores["defend"] += 30.0
            elif msg_type == "target_spotted":
                scores["attack"] += 20.0
            elif msg_type == "request_help":
                scores["defend"] += 40.0
            elif msg_type == "wounded_call":
                if personality == "healer":
                    scores["defend"] += 50.0

    # Flee scoring
    if hp_percent < 0.3:
        scores["flee"] += 50.0
    if emotion_state == "fear":
        scores["flee"] += 100.0
    if emotion_state == "cowardice":
        scores["flee"] += 80.0

    scores["flee"] += danger_level * 10.0

    # Defend scoring
    if danger_level > 0.7:
        scores["defend"] += 100.0
    if personality == "tank" or personality == "defender":
        scores["defend"] += 20.0

    scores["defend"] += danger_level * 20.0

    # Opportunistic scoring
    if boosters.size() > 0:
        scores["opportunistic"] += 30.0 + opportunity_level * 10.0
    if emotion_state == "greed":
        scores["opportunistic"] += 100.0

    if personality == "scout":
        scores["opportunistic"] += 20.0

    # Attack scoring
    if enemies.size() > 0:
        scores["attack"] += 10.0

    if danger_level > 0.7:
        scores["attack"] -= 50.0

    if emotion_state == "rage" or emotion_state == "bloodlust":
        scores["attack"] += 100.0

    if personality == "warrior" or personality == "aggressive":
        scores["attack"] += 30.0

    # Idle scoring
    scores["idle"] = 1.0

    # Baseline score based on personality
    if scores.has(personality):
        scores[personality] += 15.0

    # Validation filters
    if boosters.size() == 0:
        scores["opportunistic"] = -1000.0

    if enemies.size() == 0:
        scores["attack"] = -1000.0

    var best_action = "idle"
    var best_score = -9999.0

    var order = ["flee", "defend", "opportunistic", "attack", "idle"]
    for action in order:
        if scores[action] > best_score:
            best_score = scores[action]
            best_action = action

    if best_action == "idle":
        return personality

    return best_action
