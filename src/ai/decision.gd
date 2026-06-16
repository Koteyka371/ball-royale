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
        "chase": 0.0,
        "use skill": 0.0,
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


    if "ball_type" in self.ball and self.ball.ball_type == "neural":
        if not self.ball.has_meta("nn_weights"):
            var f = FileAccess.open("res://src/ai/nn_weights.json", FileAccess.READ)
            if f:
                var json = JSON.new()
                if json.parse(f.get_as_text()) == OK:
                    self.ball.set_meta("nn_weights", json.get_data())
                f.close()

        if self.ball.has_meta("nn_weights"):
            var weights = self.ball.get_meta("nn_weights")
            var inputs = [hp_percent, danger_level, opportunity_level, danger_level] # Threat is akin to danger in gd perception
            if perception_data.has("opportunity_score"):
                inputs[2] = perception_data["opportunity_score"]
            if perception_data.has("threat_level"):
                inputs[3] = perception_data["threat_level"]

            var hidden = []
            var idx = 0

            for h in range(8):
                var h_val = 0.0
                for i in range(4):
                    h_val += inputs[i] * float(weights[idx])
                    idx += 1
                h_val += float(weights[idx])
                idx += 1
                hidden.append(tanh(h_val))

            var outputs = []
            for o in range(6):
                var o_val = 0.0
                for h in range(8):
                    o_val += hidden[h] * float(weights[idx])
                    idx += 1
                o_val += float(weights[idx])
                idx += 1
                outputs.append(o_val)

            var actions = ["flee", "defend", "opportunistic", "attack", "chase", "use skill"]
            var max_val = outputs[0]
            var max_idx = 0
            for i in range(1, 6):
                if outputs[i] > max_val:
                    max_val = outputs[i]
                    max_idx = i
            return actions[max_idx]

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

    # Chase scoring
    if enemies.size() > 0:
        scores["chase"] += 15.0
    if personality == "assassin" or personality == "rogue" or personality == "phantom" or personality == "swarm":
        scores["chase"] += 40.0
    if emotion_state == "bloodlust":
        scores["chase"] += 80.0

    # Use skill scoring
    var difficulty = "medium"
    if "difficulty" in self.ball:
        difficulty = self.ball.difficulty

    var skill_timer = 0.0
    if "skill_timer" in self.ball:
        skill_timer = self.ball.skill_timer

    if skill_timer <= 0 and enemies.size() > 0:
        if difficulty == "easy":
            scores["use skill"] += 20.0
            if hp_percent < 0.3:
                scores["use skill"] += 30.0
        elif difficulty == "hard":
            scores["use skill"] += 60.0
            if hp_percent < 0.6:
                scores["use skill"] += 40.0
        else:
            scores["use skill"] += 40.0
            if hp_percent < 0.5:
                scores["use skill"] += 30.0

    if skill_timer > 0:
        scores["use skill"] = -1000.0

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
        scores["chase"] = -1000.0

    # Decision Quality (Noise based on difficulty)
    if difficulty == "chaos":
        for k in scores.keys():
            scores[k] = randf_range(-100.0, 100.0)
    elif difficulty == "easy":
        for k in scores.keys():
            if scores[k] > -500.0:
                scores[k] += randf_range(-20.0, 20.0)

    var best_action = "idle"
    var best_score = -9999.0

    var order = ["flee", "defend", "opportunistic", "attack", "chase", "use skill", "idle"]
    for action in order:
        if scores[action] > best_score:
            best_score = scores[action]
            best_action = action

    if best_action == "idle":
        return personality

    return best_action
