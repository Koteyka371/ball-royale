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
        "collect_booster": 0.0,
        "attack": 0.0,
        "chase": 0.0,
        "use_skill": 0.0,
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

    var team_messages = []
    if perception_data.has("team_messages"):
        team_messages = perception_data["team_messages"]

    var personality = "idle"
    if "personality" in self.ball:
        personality = self.ball.personality

    var skill_timer = 0.0
    if "skill_timer" in self.ball:
        skill_timer = self.ball.skill_timer

    # Flee scoring
    if hp_percent < 0.3:
        scores["flee"] += 50.0
    if emotion_state == "fear":
        scores["flee"] += 100.0
    if emotion_state == "cowardice":
        scores["flee"] += 80.0

    scores["flee"] += danger_level * 10.0

    var has_help_call = false
    var has_hold_call = false
    var has_target_call = false
    var has_heal_call = false

    for msg in team_messages:
        if msg.has("type"):
            var msg_type = msg["type"]
            if msg_type == "help":
                has_help_call = true
            elif msg_type == "hold":
                has_hold_call = true
            elif msg_type == "target" or msg_type == "threat":
                has_target_call = true
            elif msg_type == "heal_call":
                has_heal_call = true

    # Defend scoring
    if danger_level > 0.7:
        scores["defend"] += 100.0
    if personality == "tank" or personality == "defender" or personality == "guardian" or personality == "juggernaut":
        scores["defend"] += 30.0

    scores["defend"] += danger_level * 20.0

    if has_help_call:
        if personality in ["tank", "defender", "guardian", "juggernaut"]:
            scores["defend"] += 120.0
        else:
            scores["defend"] += 40.0
    if has_hold_call and not personality in ["tank", "warrior", "assassin"]:
        scores["defend"] += 60.0
    if has_heal_call and hp_percent < 0.5:
        scores["defend"] += 150.0

    # Collect Booster scoring
    if boosters.size() > 0:
        scores["collect_booster"] += 30.0 + opportunity_level * 10.0
    if emotion_state == "greed":
        scores["collect_booster"] += 100.0

    if personality == "scout" or personality == "rogue":
        scores["collect_booster"] += 20.0

    # Attack scoring
    if enemies.size() > 0:
        scores["attack"] += 10.0
        if has_target_call:
            scores["attack"] += 50.0

    if danger_level > 0.7:
        scores["attack"] -= 50.0

    if emotion_state == "rage" or emotion_state == "bloodlust":
        scores["attack"] += 100.0

    if personality == "warrior" or personality == "aggressive" or personality == "berserker" or personality == "bomber":
        scores["attack"] += 30.0

    # Chase scoring
    if enemies.size() > 0:
        scores["chase"] += 15.0
        if has_target_call:
            scores["chase"] += 50.0
    if personality in ["assassin", "rogue", "phantom", "swarm"]:
        scores["chase"] += 40.0
    if emotion_state == "bloodlust":
        scores["chase"] += 80.0

    # Use skill scoring
    if skill_timer <= 0 and enemies.size() > 0:
        scores["use_skill"] += 40.0
        if hp_percent < 0.5:
            scores["use_skill"] += 30.0

    # Idle scoring
    scores["idle"] = 1.0

    # Baseline score based on personality
    if scores.has(personality):
        scores[personality] += 15.0

    # Validation filters
    if boosters.size() == 0:
        scores["collect_booster"] = -1000.0

    if enemies.size() == 0:
        scores["attack"] = -1000.0
        scores["chase"] = -1000.0

    if skill_timer > 0:
        scores["use_skill"] = -1000.0

    var best_action = "idle"
    var best_score = -9999.0

    var order = ["flee", "defend", "collect_booster", "attack", "chase", "use_skill", "idle"]
    for action in order:
        if scores[action] > best_score:
            best_score = scores[action]
            best_action = action

    if best_action == "idle":
        var pers_behaviors = {
            "warrior": "attack", "tank": "defend", "assassin": "chase",
            "healer": "defend", "sniper": "attack", "bomber": "attack",
            "berserker": "attack", "juggernaut": "defend", "rogue": "chase",
            "guardian": "defend", "phantom": "chase", "swarm": "chase",
            "scout": "collect_booster", "aggressive": "attack", "defender": "defend"
        }
        if pers_behaviors.has(personality):
            return pers_behaviors[personality]
        return personality

    return best_action
