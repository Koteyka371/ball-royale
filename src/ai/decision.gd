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



var weights_cache = null

func _get_weights() -> Dictionary:
    if weights_cache != null:
        return weights_cache
    weights_cache = {}
    var file = FileAccess.open("res://src/ai/ai_weights.json", FileAccess.READ)
    if file != null:
        var text = file.get_as_text()
        file.close()
        var json = JSON.new()
        var err = json.parse(text)
        if err == OK:
            weights_cache = json.get_data()
    return weights_cache

func choose_action(perception_data: Dictionary, emotion_state: String) -> String:
    var hp_percent = 1.0
    if self.ball.has_method("get_hp_percent"):
        hp_percent = self.ball.get_hp_percent()
    elif "hp" in self.ball and "max_hp" in self.ball and float(self.ball.max_hp) > 0:
        hp_percent = float(self.ball.hp) / float(self.ball.max_hp)

    var danger_level = 0.0
    if perception_data.has("danger_level"):
        danger_level = float(perception_data["danger_level"])

    var threat_level = 0.0
    if perception_data.has("threat_level"):
        threat_level = float(perception_data["threat_level"])

    var opportunity_score = 0.0
    if perception_data.has("opportunity_score"):
        opportunity_score = float(perception_data["opportunity_score"])

    var opportunity_level = 0.0
    if perception_data.has("opportunity_level"):
        opportunity_level = float(perception_data["opportunity_level"])

    var enemies = []
    if perception_data.has("enemies"):
        enemies = perception_data["enemies"]

    var allies = []
    if perception_data.has("allies"):
        allies = perception_data["allies"]

    var boosters = []
    if perception_data.has("boosters"):
        boosters = perception_data["boosters"]

    var enemies_count = float(enemies.size())
    var allies_count = float(allies.size())
    var boosters_count = float(boosters.size())

    var skill_timer = 0.0
    if "skill_timer" in self.ball:
        skill_timer = float(self.ball.skill_timer)

    var skill_timer_ready = 1.0 if skill_timer <= 0.0 else 0.0

    var features = {
        "hp_percent": hp_percent,
        "danger_level": danger_level,
        "threat_level": threat_level,
        "opportunity_score": opportunity_score,
        "opportunity_level": opportunity_level,
        "skill_timer_ready": skill_timer_ready,
        "enemies_count": enemies_count,
        "allies_count": allies_count,
        "boosters_count": boosters_count,
        "bias": 1.0
    }

    var weights = _get_weights()

    var scores = {
        "flee": 0.0,
        "defend": 0.0,
        "collect_booster": 0.0,
        "attack": 0.0,
        "chase": 0.0,
        "use_skill": 0.0,
        "kite": 0.0,
        "flank": 0.0,
        "group_attack": 0.0,
        "idle": 0.0
    }

    for action in scores.keys():
        if weights.has(action):
            var action_weights = weights[action]
            var score = 0.0
            for feature in features.keys():
                if action_weights.has(feature):
                    score += float(action_weights[feature]) * float(features[feature])
            scores[action] = score

    var personality = ""
    if "personality" in self.ball:
        personality = self.ball.personality
    elif "personality_id" in self.ball:
        personality = self.ball.personality_id

    if typeof(personality) == TYPE_OBJECT and personality.has_method("get"):
        personality = personality.get("character", "")
    elif typeof(personality) == TYPE_STRING:
        personality = personality.to_lower()

    if scores.has(personality):
        scores[personality] += 15.0

    if emotion_state == "fear":
        scores["flee"] += 1000.0
        scores["attack"] -= 300.0
    elif emotion_state == "rage":
        scores["attack"] += 1000.0
        scores["defend"] -= 200.0
    elif emotion_state == "heroism":
        scores["defend"] += 1000.0
    elif emotion_state == "greed":
        scores["collect_booster"] += 1000.0
    elif emotion_state == "bloodlust":
        scores["chase"] += 500.0
        scores["attack"] += 500.0
    elif emotion_state == "cowardice":
        if randf() < 0.3:
            scores["flee"] += 1000.0

    if personality == "assassin":
        scores["chase"] += 1000.0

    if boosters_count == 0.0:
        scores["collect_booster"] = -1000.0
    if enemies_count == 0.0:
        scores["attack"] = -1000.0
        scores["chase"] = -1000.0
        scores["use_skill"] = -1000.0
    if skill_timer > 0.0:
        scores["use_skill"] = -1000.0

    var b_type = ""
    if "ball_type" in self.ball:
        b_type = self.ball.ball_type
    elif self.ball.has_method("get_ball_type"):
        b_type = self.ball.get_ball_type()

    b_type = b_type.to_lower()

    if b_type == "warrior" or personality == "warrior":
        scores["flee"] = -1000.0
        scores["attack"] += 100.0
        scores["chase"] += 100.0
        scores["collect_booster"] -= 20.0

    if b_type == "scout":
        scores["collect_booster"] += 40.0

    if b_type == "tank" and allies_count > 0.0:
        scores["defend"] += 50.0
        scores["collect_booster"] -= 20.0

    if perception_data.has("rival_spotted") and perception_data["rival_spotted"]:
        scores["attack"] += 200.0
        scores["chase"] += 200.0

    # Team Coordination
    if perception_data.has("team_messages"):
        var team_messages = perception_data["team_messages"]
        for msg in team_messages:
            if typeof(msg) == TYPE_DICTIONARY:
                var msg_type = msg.get("type", "")
                if msg_type == "target_spotted":
                    scores["attack"] += 150.0
                    scores["chase"] += 150.0
                elif msg_type == "request_help":
                    scores["defend"] += 200.0
                elif msg_type == "wounded_call" and b_type == "healer":
                    scores["use_skill"] += 200.0
                    scores["defend"] += 100.0
                elif msg_type == "hold_position":
                    scores["defend"] += 150.0

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
        scores["idle"] = 1000.0
        for k in scores.keys():
            if k != "idle":
                scores[k] = -1000.0

    var best_action = "idle"
    var best_score = -9999.0

    var order = ["flee", "defend", "collect_booster", "attack", "chase", "use_skill", "kite", "flank", "group_attack", "idle"]
    for action in order:
        if scores[action] > best_score:
            best_score = scores[action]
            best_action = action

    if best_action == "idle":
        var behaviors = {
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
            "swarm": "group_attack",
            "scout": "collect_booster",
            "king": "defend",
            "aggressive": "attack",
            "defender": "defend",
            "spectator": "idle"
        }
        if behaviors.has(personality):
            return behaviors[personality]
        return "idle"

    return best_action
