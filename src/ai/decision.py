from typing import Any, Dict


class Decision:
    """
    Decision system that evaluates options and chooses an action.
    Uses threat_level, opportunity_score, personality, emotional state.
    Returns best action: flee, defend, attack, use_skill, collect_booster, chase, idle.
    """

    PERSONALITY_BEHAVIORS = {
        "warrior": "attack",
        "tank": "defend",
        "assassin": "chase",
        "healer": "defend",
        "sniper": "attack",
        "bomber": "attack",
        "berserker": "attack",
        "juggernaut": "defend",
        "rogue": "chase",
        "guardian": "defend",
        "phantom": "chase",
        "swarm": "chase",
        "scout": "collect_booster",
        "aggressive": "attack",
        "defender": "defend",
    }

    def __init__(self, ball: Any, world: Any):
        self.ball = ball
        self.world = world

    def choose_action(self, perception_data: Dict[str, Any], emotion_state: str) -> str:
        hp_percent = 1.0
        if hasattr(self.ball, "get_hp_percent"):
            hp_percent = self.ball.get_hp_percent()
        elif hasattr(self.ball, "hp") and hasattr(self.ball, "max_hp"):
            hp_percent = float(self.ball.hp) / float(self.ball.max_hp)

        scores = {
            "flee": 0.0,
            "defend": 0.0,
            "collect_booster": 0.0,
            "attack": 0.0,
            "chase": 0.0,
            "use_skill": 0.0,
            "idle": 0.0,
        }

        danger_level = perception_data.get("danger_level", 0.0)
        threat_level = perception_data.get("threat_level", 0.0)
        opportunity_level = perception_data.get("opportunity_level", 0.0)
        opportunity_score = perception_data.get("opportunity_score", 0.0)
        enemies = perception_data.get("enemies", [])
        boosters = perception_data.get("boosters", [])
        allies = perception_data.get("allies", [])
        team_messages = perception_data.get("team_messages", [])

        personality = getattr(self.ball, "personality", "idle")
        skill_timer = getattr(self.ball, "skill_timer", 0.0)

        # === FLEE ===
        if hp_percent < 0.3:
            scores["flee"] += 50.0
        if emotion_state == "fear":
            scores["flee"] += 100.0
        if emotion_state == "cowardice":
            scores["flee"] += 80.0
        scores["flee"] += threat_level * 5.0
        if "call_for_wounded" in team_messages and hp_percent < 0.6:
            scores["flee"] += 60.0
        if "request_help" in team_messages and hp_percent < 0.4:
            scores["flee"] += 40.0

        # === DEFEND ===
        if danger_level > 0.7:
            scores["defend"] += 100.0
        if threat_level > 5.0:
            scores["defend"] += 50.0
        if personality in ("tank", "defender", "guardian", "juggernaut"):
            scores["defend"] += 30.0
        scores["defend"] += danger_level * 20.0
        if "hold_position" in team_messages:
            scores["defend"] += 80.0
        if "request_help" in team_messages and hp_percent >= 0.4:
            scores["defend"] += 50.0

        # === COLLECT BOOSTER ===
        if len(boosters) > 0:
            scores["collect_booster"] += 30.0 + opportunity_score * 10.0
        if emotion_state == "greed":
            scores["collect_booster"] += 100.0
        if personality in ("scout", "rogue"):
            scores["collect_booster"] += 20.0
        if len(boosters) == 0:
            scores["collect_booster"] = -1000.0

        # === ATTACK ===
        if len(enemies) > 0:
            scores["attack"] += 10.0
        if danger_level > 0.7:
            scores["attack"] -= 50.0
        if emotion_state in ("rage", "bloodlust"):
            scores["attack"] += 100.0
        if personality in ("warrior", "aggressive", "berserker", "bomber"):
            scores["attack"] += 30.0
        if "coordinate_attack" in team_messages:
            scores["attack"] += 60.0
        if "threat" in team_messages:
            scores["attack"] += 40.0
        if len(enemies) == 0:
            scores["attack"] = -1000.0

        # === CHASE ===
        if len(enemies) > 0:
            scores["chase"] += 15.0
        if personality in ("assassin", "rogue", "phantom", "swarm"):
            scores["chase"] += 40.0
        if emotion_state == "bloodlust":
            scores["chase"] += 80.0
        if "coordinate_attack" in team_messages:
            scores["chase"] += 60.0
        if "threat" in team_messages:
            scores["chase"] += 40.0
        if len(enemies) == 0:
            scores["chase"] = -1000.0

        # === USE SKILL ===
        if skill_timer <= 0 and len(enemies) > 0:
            scores["use_skill"] += 40.0
            if hp_percent < 0.5:
                scores["use_skill"] += 30.0
        if skill_timer > 0:
            scores["use_skill"] = -1000.0

        # === IDLE ===
        scores["idle"] = 1.0

        # Personality baseline
        if personality in scores:
            scores[personality] += 15.0

        # Find highest score
        best_action = "idle"
        best_score = -9999.0

        for action in ["flee", "defend", "collect_booster", "attack", "chase", "use_skill", "idle"]:
            if scores[action] > best_score:
                best_score = scores[action]
                best_action = action

        # Fall back to personality behavior instead of returning personality name
        if best_action == "idle":
            return self.PERSONALITY_BEHAVIORS.get(personality, "idle")

        return best_action
