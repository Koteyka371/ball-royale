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



static var _weights_cache = null

static func get_weights() -> Dictionary:
    if _weights_cache != null:
        return _weights_cache
    _weights_cache = {}
    var file = FileAccess.open("res://src/ai/ai_weights.json", FileAccess.READ)
    if file != null:
        var text = file.get_as_text()
        file.close()
        var json = JSON.new()
        var err = json.parse(text)
        if err == OK:
            _weights_cache = json.get_data()
    return _weights_cache

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

    var weights = get_weights()

    var scores = {
        "flee": 0.0,
        "ricochet_attack": 0.0,
            "defend": 0.0,
        "collect_booster": 0.0,
        "attack": 0.0,
        "chase": 0.0,
        "target_weak": 0.0,
        "use_skill": 0.0,
        "kite": 0.0,
        "flank": 0.0,
        "group_attack": 0.0,
        "hide_behind": 0.0,
        "idle": 0.0,
        "escort": 0.0,
        "intercept": 0.0
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

    var pref_action = ""
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
        "drone": "chase",
        "shield_drone": "escort",
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
        pref_action = behaviors[personality]

    if scores.has(pref_action):
        scores[pref_action] += 15.0

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

    # Ultimate Skill logic based on charge_level
    var charge_level = 0.0
    if "charge_level" in self.ball:
        charge_level = float(self.ball.charge_level)
    elif self.ball.has_method("get_meta") and self.ball.has_meta("charge_level"):
        charge_level = float(self.ball.get_meta("charge_level"))

    if charge_level >= 100.0:
        scores["use_skill"] += 3000.0

    var b_type = ""
    if "ball_type" in self.ball:
        b_type = self.ball.ball_type
    elif self.ball.has_method("get_ball_type"):
        b_type = self.ball.get_ball_type()

    b_type = b_type.to_lower()

    var coach_strategy = ""
    if perception_data.has("coach_strategy"):
        coach_strategy = str(perception_data["coach_strategy"]).to_lower()

    if b_type == "warrior" or personality == "warrior":
        var coach_flee = "flee" in coach_strategy or "убег" in coach_strategy or "отступ" in coach_strategy
        if not coach_flee:
            scores["flee"] = -1000.0
        scores["attack"] += 100.0
        scores["chase"] += 100.0
        scores["collect_booster"] -= 100.0

    if b_type == "ninja" or personality == "cunning":
        scores["flank"] += 150.0
        scores["attack"] -= 50.0

    if b_type == "sniper" or personality == "cautious":
        scores["kite"] += 200.0
        scores["attack"] -= 50.0

    if b_type == "scout":
        scores["collect_booster"] += 80.0

        # Flees from strong enemies
        if threat_level > 0.5:
            scores["flee"] += 150.0
            scores["attack"] -= 50.0

        # Attacks weak enemies
        if threat_level < 0.3 and opportunity_level > 0.5:
            scores["target_weak"] += 150.0
            scores["attack"] += 100.0
            scores["chase"] += 100.0
            scores["collect_booster"] -= 20.0

    if b_type == "tank" and allies_count > 0.0:
        scores["defend"] += 150.0
        scores["collect_booster"] -= 100.0

    if b_type == "healer" and allies_count > 0.0:
        scores["defend"] += 150.0
        scores["collect_booster"] -= 50.0

    # Skill Usage AI

    var has_enemy_flag = false
    for a in allies:
        if "has_flag" in a and a.has_flag:
            has_enemy_flag = true
            break

    var has_our_flag = false
    for e in enemies:
        if "has_flag" in e and e.has_flag:
            has_our_flag = true
            break

    if has_enemy_flag:
        scores["escort"] += 800.0

    if has_our_flag:
        scores["intercept"] += 800.0

    if b_type == "tank" or b_type == "healer":
        if has_enemy_flag:
            scores["escort"] += 200.0


    if b_type == "assassin" or b_type == "ninja":
        if has_our_flag:
            scores["intercept"] += 200.0

    # King of the Hill / Zone Mode prioritization
    var game_mode_name = ""
    if self.world != null and "game_mode" in self.world and self.world.game_mode != null:
        if "name" in self.world.game_mode:
            game_mode_name = self.world.game_mode.name.to_lower()

    if "king of the hill" in game_mode_name or "zone" in game_mode_name:
        if not scores.has("hold_zone"):
            scores["hold_zone"] = 0.0
        scores["hold_zone"] += 1500.0
        scores["attack"] -= 500.0
        scores["chase"] -= 500.0

    if skill_timer <= 0.0:
        if b_type == "warrior" and enemies_count >= 2.0:
            scores["use_skill"] += 300.0
        elif b_type == "scout" and (danger_level > 0.5 or opportunity_level > 0.5):
            scores["use_skill"] += 200.0
        elif b_type == "tank" and hp_percent < 0.5:
            scores["use_skill"] += 300.0
        elif b_type == "healer" and allies_count > 0.0:
            scores["use_skill"] += 250.0
        elif b_type == "sniper" and threat_level > 0.3:
            scores["use_skill"] += 200.0
        elif b_type == "bomber" and enemies_count >= 3.0:
            scores["use_skill"] += 400.0
        elif b_type == "ninja" and opportunity_level > 0.5:
            scores["use_skill"] += 200.0
        elif b_type == "king" and allies_count > 0.0:
            scores["use_skill"] += 200.0

    # Ball Relationships - Balls remember each other
    # Rivalry skill: attacked me before -> attack on sight
    if perception_data.has("rival_spotted") and perception_data["rival_spotted"]:
        scores["attack"] += 275.0
        scores["chase"] += 275.0

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

    if coach_strategy != "":
        if "attack" in coach_strategy or "атак" in coach_strategy:
            scores["attack"] += 2000.0
            scores["chase"] += 2000.0
        elif "defend" in coach_strategy or "защищ" in coach_strategy:
            scores["defend"] += 2000.0
        elif "flee" in coach_strategy or "убег" in coach_strategy or "отступ" in coach_strategy:
            scores["flee"] += 2000.0
        elif "booster" in coach_strategy or "собир" in coach_strategy or "collect" in coach_strategy:
            scores["collect_booster"] += 2000.0
        elif "skill" in coach_strategy or "скилл" in coach_strategy or "способн" in coach_strategy:
            scores["use_skill"] += 2000.0

    if b_type == "spectator":
        scores["idle"] = 1000.0
        for k in scores.keys():
            if k != "idle":
                scores[k] = -1000.0

    var best_action = "idle"
    var best_score = -9999.0

    var difficulty = "medium"
    if "difficulty" in self.ball:
        difficulty = str(self.ball.difficulty).to_lower()

    if difficulty == "chaos":
        if skill_timer <= 0.0 and randf() < 0.8:
            best_action = "use_skill"
            if scores.has("use_skill"):
                best_score = scores["use_skill"]
            else:
                best_score = 0.0
        else:
            var possible = []
            for k in scores.keys():
                if float(scores[k]) > -500.0:
                    possible.append(k)
            if possible.size() > 0:
                best_action = possible[randi() % possible.size()]
            else:
                best_action = "idle"

            if scores.has(best_action):
                best_score = float(scores[best_action])
            else:
                best_score = 0.0
    else:
        var action_order = ["ricochet_attack", "hold_zone", "intercept", "escort", "flee", "defend", "collect_booster", "attack", "target_weak", "chase", "use_skill", "kite", "flank", "group_attack", "hide_behind", "idle"]
        var possible_actions = []
        for k in scores.keys():
            if float(scores[k]) > -500.0:
                possible_actions.append(k)

        var sorted_actions = []
        for a in possible_actions:
            var inserted = false
            for i in range(sorted_actions.size()):
                var score_a = float(scores[a])
                var score_b = float(scores[sorted_actions[i]])
                if score_a > score_b:
                    sorted_actions.insert(i, a)
                    inserted = true
                    break
                elif score_a == score_b:
                    var index_a = action_order.find(a)
                    var index_b = action_order.find(sorted_actions[i])
                    if index_a < index_b:
                        sorted_actions.insert(i, a)
                        inserted = true
                        break
            if not inserted:
                sorted_actions.append(a)

        if sorted_actions.size() == 0:
            sorted_actions = ["idle"]

        if difficulty == "easy":
            var top_actions = []
            for i in range(min(3, sorted_actions.size())):
                top_actions.append(sorted_actions[i])

            if "use_skill" in top_actions and randf() < 0.5:
                top_actions.erase("use_skill")

            if top_actions.size() == 0:
                top_actions = ["idle"]

            if randf() < 0.3:
                best_action = top_actions[randi() % top_actions.size()]
            else:
                best_action = top_actions[0]
        elif difficulty == "medium":
            var top_actions = []
            for i in range(min(5, sorted_actions.size())):
                top_actions.append(sorted_actions[i])

            if randf() < 0.1 and top_actions.size() > 1:
                best_action = top_actions[randi() % top_actions.size()]
            else:
                best_action = top_actions[0]
        else:
            best_action = sorted_actions[0]

        if scores.has(best_action):
            best_score = scores[best_action]
        else:
            best_score = 0.0

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
        "drone": "chase",
        "shield_drone": "escort",
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
