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
    elif "hp" in self.ball and "max_hp" in self.ball:
        hp_percent = float(self.ball.hp) / float(self.ball.max_hp)

    var scores = {
        "flee": 0.0,
        "defend": 0.0,
        "collect_booster": 0.0,
        "attack": 0.0,
        "chase": 0.0,
        "use_skill": 0.0,
        "kite": 0.0,
        "flank": 0.0,
        "idle": 0.0
    }

    var danger_level = 0.0
    if perception_data.has("danger_level"):
        danger_level = perception_data["danger_level"]

    var opportunity_level = 0.0
    if perception_data.has("opportunity_level"):
        opportunity_level = perception_data["opportunity_level"]

    var opportunity_score = 0.0
    if perception_data.has("opportunity_score"):
        opportunity_score = perception_data["opportunity_score"]

    var enemies = []
    if perception_data.has("enemies"):
        enemies = perception_data["enemies"]

    var boosters = []
    if perception_data.has("boosters"):
        boosters = perception_data["boosters"]

    var allies = []
    if perception_data.has("allies"):
        allies = perception_data["allies"]

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

    if personality == "curious":
        var strong_enemies = 0
        for e in enemies:
            var e_hp_pct = 1.0
            if e.has_method("get_hp_percent"):
                e_hp_pct = e.get_hp_percent()
            elif "hp" in e and "max_hp" in e and float(e.max_hp) > 0:
                e_hp_pct = float(e.hp) / float(e.max_hp)
            if e_hp_pct >= 0.3:
                strong_enemies += 1
        if strong_enemies > 0:
            scores["flee"] += strong_enemies * 20.0

    # Defend scoring
    if danger_level > 0.7:
        scores["defend"] += 100.0
    if personality == "tank" or personality == "defender" or personality == "guardian" or personality == "juggernaut" or personality == "leader":
        scores["defend"] += 30.0

    if personality == "tank" and allies.size() > 0:
        var needs_protection = false
        for ally in allies:
            var a_type = ""
            if "ball_type" in ally:
                a_type = str(ally.ball_type).to_lower()
            elif ally.has_method("get") and ally.get("BALL_TYPE") != null:
                a_type = str(ally.get("BALL_TYPE")).to_lower()

            var a_hp_pct = 1.0
            if ally.has_method("get_hp_percent"):
                a_hp_pct = ally.get_hp_percent()
            elif "hp" in ally and "max_hp" in ally and float(ally.max_hp) > 0:
                a_hp_pct = float(ally.hp) / float(ally.max_hp)

            if a_type == "healer" or a_hp_pct < 0.5:
                needs_protection = true
                break
        if needs_protection:
            scores["defend"] += 50.0

    scores["defend"] += danger_level * 20.0
    if emotion_state == "heroism":
        scores["defend"] += 80.0
    if hp_percent < 0.5 and allies.size() > 0:
        scores["defend"] += allies.size() * 10.0

    if personality == "leader" and allies.size() > 0:
        var weak_allies = 0
        for a in allies:
            var a_hp_pct = 1.0
            if a.has_method("get_hp_percent"):
                a_hp_pct = a.get_hp_percent()
            elif "hp" in a and "max_hp" in a and float(a.max_hp) > 0:
                a_hp_pct = float(a.hp) / float(a.max_hp)
            if a_hp_pct < 0.5:
                weak_allies += 1
        if weak_allies > 0:
            scores["defend"] += weak_allies * 30.0

    # Collect booster scoring
    if boosters.size() > 0:
        scores["collect_booster"] += 30.0 + (opportunity_score + opportunity_level) * 10.0
    if emotion_state == "greed":
        scores["collect_booster"] += 100.0

    if personality == "scout" or personality == "rogue":
        scores["collect_booster"] += 20.0

    # Attack scoring
    if enemies.size() > 0:
        scores["attack"] += 10.0

    if danger_level > 0.7:
        scores["attack"] -= 50.0

    if emotion_state == "rage" or emotion_state == "bloodlust":
        scores["attack"] += 100.0

    if emotion_state == "heroism":
        scores["attack"] += 50.0

    if personality == "warrior" or personality == "aggressive" or personality == "berserker" or personality == "bomber":
        scores["attack"] += 30.0

    if allies.size() > enemies.size():
        scores["attack"] += (allies.size() - enemies.size()) * 15.0

    if personality == "curious":
        var weak_enemies = 0
        for e in enemies:
            var e_hp_pct = 1.0
            if e.has_method("get_hp_percent"):
                e_hp_pct = e.get_hp_percent()
            elif "hp" in e and "max_hp" in e and float(e.max_hp) > 0:
                e_hp_pct = float(e.hp) / float(e.max_hp)
            if e_hp_pct < 0.3:
                weak_enemies += 1
        if weak_enemies > 0:
            scores["attack"] += weak_enemies * 20.0

    # Chase scoring
    if enemies.size() > 0:
        scores["chase"] += 15.0
    if personality == "assassin" or personality == "rogue" or personality == "phantom" or personality == "swarm":
        scores["chase"] += 40.0
    if emotion_state == "bloodlust":
        scores["chase"] += 80.0

    var b_type = ""
    if "ball_type" in self.ball:
        b_type = self.ball.ball_type
    elif self.ball.has_method("get_ball_type"):
        b_type = self.ball.get_ball_type()

    if b_type.to_lower() == "scout":
        var a_timer = 0.0
        if "attack_timer" in self.ball:
            a_timer = float(self.ball.attack_timer)
        if a_timer <= 0.0:
            scores["flank"] += 60.0

    if b_type.to_lower() == "sniper" and enemies.size() > 0:
        scores["kite"] += 100.0

    if b_type.to_lower() == "ninja":
        var a_timer = 0.0
        if "attack_timer" in self.ball:
            a_timer = float(self.ball.attack_timer)
        if a_timer > 0.0:
            scores["flee"] += 200.0
        else:
            scores["flank"] += 100.0

    if personality == "curious":
        var weak_enemies = 0
        for e in enemies:
            var e_hp_pct = 1.0
            if e.has_method("get_hp_percent"):
                e_hp_pct = e.get_hp_percent()
            elif "hp" in e and "max_hp" in e and float(e.max_hp) > 0:
                e_hp_pct = float(e.hp) / float(e.max_hp)
            if e_hp_pct < 0.3:
                weak_enemies += 1
        if weak_enemies > 0:
            scores["chase"] += weak_enemies * 25.0

    # Use skill scoring
    var difficulty = "medium"
    if "difficulty" in self.ball:
        difficulty = self.ball.difficulty

    var skill_timer = 0.0
    if "skill_timer" in self.ball:
        skill_timer = self.ball.skill_timer

    var intent_flee = scores["flee"] > max(scores["defend"], max(scores["attack"], max(scores["chase"], scores.get("collect_booster", 0.0))))
    var intent_chase = scores["chase"] > max(scores["flee"], max(scores["defend"], max(scores["attack"], scores.get("collect_booster", 0.0))))

    if skill_timer <= 0 and b_type.to_lower() == "tank":
        var first_hit_taken = false
        if "first_hit_taken" in self.ball:
            first_hit_taken = self.ball.first_hit_taken
        if first_hit_taken or hp_percent < 1.0 or danger_level > 0.5:
            scores["use_skill"] += 100.0

    if skill_timer <= 0 and enemies.size() > 0:
        if difficulty == "easy":
            scores["use_skill"] += 20.0
            if hp_percent < 0.3:
                scores["use_skill"] += 30.0
        elif difficulty == "hard":
            scores["use_skill"] += 60.0
            if hp_percent < 0.6:
                scores["use_skill"] += 40.0
        else:
            scores["use_skill"] += 40.0
            if hp_percent < 0.5:
                scores["use_skill"] += 30.0

        var skill_name = ""
        if "skill" in self.ball:
            skill_name = self.ball.skill
        if (skill_name == "dash" or skill_name == "stealth") and (intent_flee or intent_chase):
            scores["use_skill"] += 50.0
        if skill_name == "command" and allies.size() > 0:
            scores["use_skill"] += 40.0

    if skill_timer > 0:
        scores["use_skill"] = -1000.0

    # Idle scoring
    scores["idle"] = 1.0

    # Baseline score based on personality
    if scores.has(personality):
        scores[personality] += 15.0

    if typeof(personality) == TYPE_OBJECT and personality.has_method("get_decision_modifiers"):
        var mods = personality.get_decision_modifiers()
        for k in mods.keys():
            if scores.has(k):
                scores[k] += mods[k]

    # Validation filters
    if boosters.size() == 0:
        scores["collect_booster"] = -1000.0

    if enemies.size() == 0:
        scores["attack"] = -1000.0
        scores["chase"] = -1000.0

    if b_type.to_lower() == "warrior":
        scores["flee"] = -1000.0
        scores["attack"] += 100.0
        scores["chase"] += 100.0

    # Coach Mode Overrides
    if "coach_strategy" in self.ball:
        var coach_strategy = self.ball.coach_strategy
        if scores.has(coach_strategy):
            scores[coach_strategy] += 500.0

    # Decision Quality (Noise based on difficulty)
    if difficulty == "chaos":
        for k in scores.keys():
            scores[k] = randf_range(-100.0, 100.0)
    elif difficulty == "easy":
        for k in scores.keys():
            if scores[k] > -500.0:
                scores[k] += randf_range(-20.0, 20.0)

    if b_type.to_lower() == "spectator":
        scores["idle"] = 1000.0
        for k in scores.keys():
            if k != "idle":
                scores[k] = -1000.0

    var best_action = "idle"
    var best_score = -9999.0

    var order = ["flee", "defend", "collect_booster", "attack", "chase", "use_skill", "kite", "flank", "idle"]
    for action in order:
        if scores[action] > best_score:
            best_score = scores[action]
            best_action = action

    if best_action == "idle":
        return personality

    return best_action
