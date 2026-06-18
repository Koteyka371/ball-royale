class_name DecisionLayer
extends RefCounted

# Decision system that evaluates options and chooses an action.
# Weighs threat level, opportunity, personality, emotional state.
# Returns best action: chase, flee, attack, use_skill, collect_booster, defend.

var ball = null
var world = null

func _init(ball_ref, world_ref):
    self.ball = ball_ref
    self.world = world_ref

func choose_action(perception_data: Dictionary, emotion_state: String) -> String:
    var hp_percent = 1.0
    if self.ball.has_method("get_hp_percent"):
        hp_percent = self.ball.get_hp_percent()
    elif "hp" in self.ball and "max_hp" in self.ball and float(self.ball.max_hp) > 0:
        hp_percent = float(self.ball.hp) / float(self.ball.max_hp)

    var danger_level = perception_data.get("danger_level", 0.0)
    var opportunity_level = perception_data.get("opportunity_level", 0.0)
    var threat_level = perception_data.get("threat_level", 0.0)
    var opportunity_score = perception_data.get("opportunity_score", 0.0)

    var enemies = perception_data.get("enemies", [])
    var boosters = perception_data.get("boosters", [])
    var allies = perception_data.get("allies", [])

    var enemies_count = enemies.size()
    var allies_count = allies.size()
    var boosters_count = boosters.size()

    var skill_timer = 0.0
    if "skill_timer" in self.ball:
        skill_timer = float(self.ball.skill_timer)
    var skill_ready = 1.0 if skill_timer <= 0.0 else 0.0

    var emotion_fear = 1.0 if emotion_state == "fear" else 0.0
    var emotion_greed = 1.0 if emotion_state == "greed" else 0.0
    var emotion_rage = 1.0 if emotion_state == "rage" or emotion_state == "bloodlust" else 0.0
    var emotion_heroism = 1.0 if emotion_state == "heroism" else 0.0

    var p_str = "idle"
    var personality = "idle"
    if "personality" in self.ball:
        personality = self.ball.personality

    if typeof(personality) == TYPE_STRING:
        p_str = personality.to_lower()
    elif typeof(personality) == TYPE_OBJECT and "character" in personality:
        p_str = str(personality.character).to_lower()

    var personality_assassin = 1.0 if p_str in ["assassin", "rogue", "phantom", "swarm"] else 0.0
    var personality_scout = 1.0 if p_str in ["scout", "rogue"] else 0.0
    var personality_warrior = 1.0 if p_str in ["warrior", "aggressive", "berserker", "bomber"] else 0.0

    var inputs = [
        hp_percent, danger_level, opportunity_level, threat_level, opportunity_score,
        enemies_count, allies_count, boosters_count, skill_ready,
        emotion_fear, emotion_greed, emotion_rage, emotion_heroism,
        personality_assassin, personality_scout, personality_warrior
    ]

    var weights = null
    var biases = null

    if "ai_weights" in self.ball:
        weights = self.ball.ai_weights
    elif self.ball.has_meta("ai_weights"):
        weights = self.ball.get_meta("ai_weights")

    if "ai_biases" in self.ball:
        biases = self.ball.ai_biases
    elif self.ball.has_meta("ai_biases"):
        biases = self.ball.get_meta("ai_biases")

    if weights == null or biases == null:
        var file = FileAccess.open("res://src/ai/ai_weights.json", FileAccess.READ)
        if file != null:
            var content = file.get_as_text()
            file.close()
            var json = JSON.new()
            var error = json.parse(content)
            if error == OK:
                var data = json.get_data()
                if data.has("weights") and data.has("biases"):
                    weights = data["weights"]
                    biases = data["biases"]
                    if self.ball.has_method("set_meta"):
                        self.ball.set_meta("ai_weights", weights)
                        self.ball.set_meta("ai_biases", biases)

    if weights == null or biases == null:
        weights = [
            [-50, 50, 0, 20, 0, 10, -10, 0, 0, 100, -10, -10, -10, 0, 0, -20],
            [10, 100, 0, 20, 0, 5, 20, 0, 0, 0, 0, 0, 50, 0, 0, 0],
            [0, -10, 30, -10, 50, -5, 0, 30, 0, -10, 100, -10, -10, 0, 50, -10],
            [20, -20, 0, -10, 0, 20, 20, 0, 0, -20, -10, 100, 20, 0, 0, 50],
            [10, -10, 0, 0, 0, 10, 0, 0, 0, -20, -10, 30, 0, 80, 0, 20],
            [-20, 20, 0, 20, 0, 10, 0, 0, 100, 10, 0, 10, 10, 10, 10, 10],
            [0, 20, 0, 10, 0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, -10, 0, 0, 0, 5, 5, 0, 0, -10, 0, 10, 0, 20, 20, 0],
            [-10, -10, -10, -10, -10, -10, -10, -10, 0, 0, 0, 0, 0, 0, 0, 0]
        ]
        biases = [0, 0, 0, 0, 0, -50, 0, 0, 5]

    var actions = ["flee", "defend", "collect_booster", "attack", "chase", "use_skill", "kite", "flank", "idle"]
    var scores = {}
    for action in actions:
        scores[action] = -9999.0

    for i in range(actions.size()):
        if i < biases.size():
            var score = biases[i]
            for j in range(inputs.size()):
                if i < weights.size() and j < weights[i].size():
                    score += inputs[j] * weights[i][j]
            scores[actions[i]] = score

    # Validation logic and overrides
    var b_type = ""
    if "ball_type" in self.ball:
        b_type = str(self.ball.ball_type).to_lower()
    elif self.ball.has_method("get_ball_type"):
        b_type = str(self.ball.get_ball_type()).to_lower()

    if boosters_count == 0:
        scores["collect_booster"] = -1000.0

    if enemies_count == 0:
        scores["attack"] = -1000.0
        scores["chase"] = -1000.0

    if skill_timer > 0.0:
        scores["use_skill"] = -1000.0

    if b_type == "warrior":
        scores["flee"] = -1000.0
        scores["attack"] += 100.0
        scores["chase"] += 100.0

    var coach_strategy = ""
    if perception_data.has("coach_strategy"):
        coach_strategy = str(perception_data["coach_strategy"]).to_lower()

    if coach_strategy != "":
        if "attack" in coach_strategy or "атак" in coach_strategy:
            scores["attack"] += 500.0
            scores["chase"] += 500.0
        elif "defend" in coach_strategy or "защищ" in coach_strategy:
            scores["defend"] += 500.0
        elif "flee" in coach_strategy or "убег" in coach_strategy or "отступ" in coach_strategy:
            scores["flee"] += 500.0
        elif "booster" in coach_strategy or "собир" in coach_strategy or "collect" in coach_strategy:
            scores["collect_booster"] += 500.0
        elif "skill" in coach_strategy or "скилл" in coach_strategy or "способн" in coach_strategy:
            scores["use_skill"] += 500.0

    if b_type == "spectator":
        for k in scores.keys():
            scores[k] = -1000.0
        scores["idle"] = 1000.0

    var best_score = -9999.0
    var best_action = "idle"

    for action in ["flee", "defend", "collect_booster", "attack", "chase", "use_skill", "kite", "flank", "idle"]:
        if scores.get(action, -9999.0) > best_score:
            best_score = scores[action]
            best_action = action

    if best_action == "idle":
        var PERSONALITY_BEHAVIORS = {
            "warrior": "attack",
            "tank": "defend",
            "assassin": "chase",
            "healer": "defend",
            "sniper": "kite",
            "bomber": "attack",
            "berserker": "attack",
            "juggernaut": "defend",
            "rogue": "chase",
            "guardian": "defend",
            "phantom": "chase",
            "swarm": "chase",
            "scout": "collect_booster",
            "king": "defend",
            "aggressive": "attack",
            "defender": "defend",
            "spectator": "idle"
        }
        if p_str in PERSONALITY_BEHAVIORS:
            return PERSONALITY_BEHAVIORS[p_str]

    return best_action
