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
        "spectator": "idle",
    }

    def __init__(self, ball: Any, world: Any):
        self.ball = ball
        self.world = world

    def choose_action(self, perception_data: Dict[str, Any], emotion_state: str) -> str:
        import os
        import json

        hp_percent = 1.0
        if hasattr(self.ball, "get_hp_percent"):
            hp_percent = self.ball.get_hp_percent()
        elif hasattr(self.ball, "hp") and hasattr(self.ball, "max_hp") and self.ball.max_hp > 0:
            hp_percent = float(self.ball.hp) / float(self.ball.max_hp)

        danger_level = perception_data.get("danger_level", 0.0)
        opportunity_level = perception_data.get("opportunity_level", 0.0)
        threat_level = perception_data.get("threat_level", 0.0)
        opportunity_score = perception_data.get("opportunity_score", 0.0)

        enemies = perception_data.get("enemies", [])
        boosters = perception_data.get("boosters", [])
        allies = perception_data.get("allies", [])

        enemies_count = len(enemies)
        allies_count = len(allies)
        boosters_count = len(boosters)

        skill_timer = getattr(self.ball, "skill_timer", 0.0)
        skill_ready = 1.0 if skill_timer <= 0.0 else 0.0

        emotion_fear = 1.0 if emotion_state == "fear" else 0.0
        emotion_greed = 1.0 if emotion_state == "greed" else 0.0
        emotion_rage = 1.0 if emotion_state in ("rage", "bloodlust") else 0.0
        emotion_heroism = 1.0 if emotion_state == "heroism" else 0.0

        personality = getattr(self.ball, "personality", "idle")
        if isinstance(personality, str):
            p_str = personality.lower()
        elif hasattr(personality, "character"):
            p_str = personality.character.lower()
        else:
            p_str = "idle"

        personality_assassin = 1.0 if p_str in ("assassin", "rogue", "phantom", "swarm") else 0.0
        personality_scout = 1.0 if p_str in ("scout", "rogue") else 0.0
        personality_warrior = 1.0 if p_str in ("warrior", "aggressive", "berserker", "bomber") else 0.0

        inputs = [
            hp_percent, danger_level, opportunity_level, threat_level, opportunity_score,
            enemies_count, allies_count, boosters_count, skill_ready,
            emotion_fear, emotion_greed, emotion_rage, emotion_heroism,
            personality_assassin, personality_scout, personality_warrior
        ]

        # Load weights
        weights = getattr(self.ball, "ai_weights", None)
        biases = getattr(self.ball, "ai_biases", None)
        actions = ["flee", "defend", "collect_booster", "attack", "chase", "use_skill", "kite", "flank", "idle"]

        if weights is None or biases is None:
            filepath = os.path.join(os.path.dirname(__file__), "ai_weights.json")
            if os.path.exists(filepath):
                try:
                    with open(filepath, "r") as f:
                        data = json.load(f)
                        weights = data["weights"]
                        biases = data["biases"]
                        self.ball.ai_weights = weights
                        self.ball.ai_biases = biases
                except Exception:
                    pass

        if weights is None or biases is None:
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

        scores = {action: -9999.0 for action in actions}

        for i, action in enumerate(actions):
            if i < len(biases):
                score = biases[i]
                for j in range(len(inputs)):
                    if i < len(weights) and j < len(weights[i]):
                        score += inputs[j] * weights[i][j]
                scores[action] = score

        # Validation logic and overrides
        b_type = getattr(self.ball, "ball_type", getattr(self.ball.__class__, "BALL_TYPE", "")).lower()

        if boosters_count == 0:
            scores["collect_booster"] = -1000.0

        if enemies_count == 0:
            scores["attack"] = -1000.0
            scores["chase"] = -1000.0

        if skill_timer > 0:
            scores["use_skill"] = -1000.0

        if b_type == "warrior":
            scores["flee"] = -1000.0
            scores["attack"] += 100.0
            scores["chase"] += 100.0

        coach_strategy = perception_data.get("coach_strategy", "")
        if coach_strategy and isinstance(coach_strategy, str):
            c_lower = coach_strategy.lower()
            if "attack" in c_lower or "атак" in c_lower:
                scores["attack"] += 500.0
                scores["chase"] += 500.0
            elif "defend" in c_lower or "защищ" in c_lower:
                scores["defend"] += 500.0
            elif "flee" in c_lower or "убег" in c_lower or "отступ" in c_lower:
                scores["flee"] += 500.0
            elif "booster" in c_lower or "собир" in c_lower or "collect" in c_lower:
                scores["collect_booster"] += 500.0
            elif "skill" in c_lower or "скилл" in c_lower or "способн" in c_lower:
                scores["use_skill"] += 500.0

        if b_type == "spectator":
            for k in scores.keys():
                scores[k] = -1000.0
            scores["idle"] = 1000.0

        best_score = -9999.0
        best_action = "idle"

        for action in ["flee", "defend", "collect_booster", "attack", "chase", "use_skill", "kite", "flank", "idle"]:
            if scores.get(action, -9999.0) > best_score:
                best_score = scores[action]
                best_action = action

        if best_action == "idle" and p_str in self.PERSONALITY_BEHAVIORS:
            return self.PERSONALITY_BEHAVIORS[p_str]

        return best_action
