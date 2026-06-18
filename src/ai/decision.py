import random
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
            "kite": 0.0,
            "flank": 0.0,
            "idle": 0.0,
        }

        danger_level = perception_data.get("danger_level", 0.0)
        threat_level = perception_data.get("threat_level", 0.0)
        opportunity_level = perception_data.get("opportunity_level", 0.0)
        opportunity_score = perception_data.get("opportunity_score", 0.0)
        enemies = perception_data.get("enemies", [])
        boosters = perception_data.get("boosters", [])
        allies = perception_data.get("allies", [])

        personality = getattr(self.ball, "personality", "idle")
        skill_timer = getattr(self.ball, "skill_timer", 0.0)
        team_messages = perception_data.get("team_messages", [])

        # Process team messages
        for msg in team_messages:
            if isinstance(msg, dict):
                msg_type = msg.get("type")
                if msg_type == "hold_position":
                    scores["defend"] += 30.0
                elif msg_type == "target_spotted":
                    scores["attack"] += 20.0
                    scores["chase"] += 20.0
                elif msg_type == "request_help":
                    scores["defend"] += 40.0
                elif msg_type == "wounded_call":
                    if personality == "healer":
                        scores["defend"] += 50.0

        # === FLEE ===
        if hp_percent < 0.3:
            scores["flee"] += 50.0
        if emotion_state == "fear":
            scores["flee"] += 100.0
        if emotion_state == "cowardice":
            scores["flee"] += 80.0
        scores["flee"] += threat_level * 5.0

        if personality == "curious":
            strong_enemies = sum(1 for e in enemies if (e.hp / e.max_hp if hasattr(e, "hp") and hasattr(e, "max_hp") and e.max_hp > 0 else 1.0) >= 0.3)
            if strong_enemies > 0:
                scores["flee"] += strong_enemies * 20.0

        # === DEFEND ===
        if danger_level > 0.7:
            scores["defend"] += 100.0
        if threat_level > 5.0:
            scores["defend"] += 50.0
        if personality in ("tank", "defender", "guardian", "juggernaut", "leader"):
            scores["defend"] += 30.0

        if personality == "tank" and len(allies) > 0:
            needs_protection = False
            for ally in allies:
                a_type = getattr(ally, "ball_type", getattr(ally.__class__, "BALL_TYPE", "")).lower()
                a_hp_pct = 1.0
                if hasattr(ally, "get_hp_percent"):
                    a_hp_pct = ally.get_hp_percent()
                elif hasattr(ally, "hp") and hasattr(ally, "max_hp"):
                    a_hp_pct = float(ally.hp) / float(ally.max_hp) if ally.max_hp > 0 else 1.0
                if a_type == "healer" or a_hp_pct < 0.5:
                    needs_protection = True
                    break
            if needs_protection:
                scores["defend"] += 50.0

        scores["defend"] += danger_level * 20.0
        if emotion_state == "heroism":
            scores["defend"] += 80.0
        if hp_percent < 0.5 and len(allies) > 0:
            scores["defend"] += len(allies) * 10.0

        if personality == "leader" and len(allies) > 0:
            weak_allies = sum(1 for a in allies if (a.hp / a.max_hp if hasattr(a, "hp") and hasattr(a, "max_hp") and a.max_hp > 0 else 1.0) < 0.5)
            if weak_allies > 0:
                scores["defend"] += weak_allies * 30.0

        # === COLLECT BOOSTER ===
        if len(boosters) > 0:
            scores["collect_booster"] += 30.0 + (opportunity_score + opportunity_level) * 10.0
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
        if emotion_state == "heroism":
            scores["attack"] += 50.0
        if personality in ("warrior", "aggressive", "berserker", "bomber"):
            scores["attack"] += 30.0
        if len(allies) > len(enemies):
            scores["attack"] += (len(allies) - len(enemies)) * 15.0
        if personality == "curious":
            weak_enemies = sum(1 for e in enemies if (e.hp / e.max_hp if hasattr(e, "hp") and hasattr(e, "max_hp") and e.max_hp > 0 else 1.0) < 0.3)
            if weak_enemies > 0:
                scores["attack"] += weak_enemies * 20.0
        if len(enemies) == 0:
            scores["attack"] = -1000.0

        # === CHASE ===
        if len(enemies) > 0:
            scores["chase"] += 15.0
        if personality in ("assassin", "rogue", "phantom", "swarm"):
            scores["chase"] += 40.0
        if emotion_state == "bloodlust":
            scores["chase"] += 80.0


        # === FLANK LOGIC ===
        b_type = getattr(self.ball, "ball_type", getattr(self.ball.__class__, "BALL_TYPE", "")).lower()
        if b_type == "scout":
            if getattr(self.ball, "attack_timer", 0.0) <= 0.0:
                scores["flank"] += 60.0

        # === KITE ===
        b_type = getattr(self.ball, "ball_type", getattr(self.ball.__class__, "BALL_TYPE", "")).lower()
        if b_type == "sniper" and len(enemies) > 0:
            scores["kite"] += 100.0
        if personality == "curious":
            weak_enemies = sum(1 for e in enemies if (e.hp / e.max_hp if hasattr(e, "hp") and hasattr(e, "max_hp") and e.max_hp > 0 else 1.0) < 0.3)
            if weak_enemies > 0:
                scores["chase"] += weak_enemies * 25.0
        if len(enemies) == 0:
            scores["chase"] = -1000.0

        # === NINJA LOGIC ===
        b_type = getattr(self.ball, "ball_type", getattr(self.ball.__class__, "BALL_TYPE", "")).lower()
        if b_type == "ninja":
            if getattr(self.ball, "attack_timer", 0.0) > 0.0:
                scores["flee"] += 200.0
            else:
                scores["flank"] += 100.0

        # === USE SKILL ===
        difficulty = getattr(self.ball, "difficulty", "medium")

        # Determine intent (flee or chase)
        intent_flee = scores["flee"] > max(scores["defend"], scores["attack"], scores["chase"], scores["collect_booster"])
        intent_chase = scores["chase"] > max(scores["flee"], scores["defend"], scores["attack"], scores["collect_booster"])

        b_type = getattr(self.ball, "ball_type", getattr(self.ball.__class__, "BALL_TYPE", "")).lower()
        if skill_timer <= 0 and b_type == "tank":
            first_hit_taken = getattr(self.ball, "first_hit_taken", False)
            if first_hit_taken or hp_percent < 1.0 or danger_level > 0.5:
                scores["use_skill"] += 100.0

        if skill_timer <= 0 and len(enemies) > 0:
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

            skill_name = getattr(self.ball, "skill", "")
            if skill_name in ("dash", "stealth", "flank") and (intent_flee or intent_chase):
                scores["use_skill"] += 50.0
            if skill_name == "command" and len(allies) > 0:
                scores["use_skill"] += 40.0

        if skill_timer > 0:
            scores["use_skill"] = -1000.0

        # === IDLE ===
        scores["idle"] = 1.0

        # === COACH MODE OVERRIDE ===
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


        # Personality baseline
        if personality in scores:
            scores[personality] += 15.0

        if hasattr(personality, "get_decision_modifiers"):
            mods = personality.get_decision_modifiers()
            for action_key, mod_val in mods.items():
                if action_key in scores:
                    scores[action_key] += mod_val

        # Warrior override: Never flees, high attack/chase priority
        b_type = getattr(self.ball, "ball_type", getattr(self.ball.__class__, "BALL_TYPE", "")).lower()
        if b_type == "warrior":
            scores["flee"] = -1000.0
            scores["attack"] += 100.0
            scores["chase"] += 100.0
            scores["collect_booster"] -= 20.0

        # Scout override: Priorities for boosters and weak enemies
        if b_type == "scout":
            scores["collect_booster"] += 40.0
            weak_enemies = sum(1 for e in enemies if (e.hp / e.max_hp if hasattr(e, "hp") and hasattr(e, "max_hp") and e.max_hp > 0 else 1.0) < 0.3)
            strong_enemies = sum(1 for e in enemies if (e.hp / e.max_hp if hasattr(e, "hp") and hasattr(e, "max_hp") and e.max_hp > 0 else 1.0) >= 0.7)
            if weak_enemies > 0:
                scores["chase"] += weak_enemies * 30.0
            if strong_enemies > 0:
                scores["chase"] -= strong_enemies * 30.0

        # Tank override: Prioritize defend when allies are near
        if b_type == "tank" and len(allies) > 0:
            scores["defend"] += 50.0
            scores["collect_booster"] -= 20.0

        # Healer override: Prioritize defend (healing) over attack when allies are wounded
        if b_type == "healer":
            wounded_allies = sum(1 for a in allies if (a.hp / a.max_hp if hasattr(a, "hp") and hasattr(a, "max_hp") and a.max_hp > 0 else 1.0) < 1.0)
            if wounded_allies > 0:
                scores["defend"] += 60.0
                scores["attack"] -= 50.0

        # Decision Quality (Noise based on difficulty)
        if difficulty == "chaos":
            for k in scores.keys():
                scores[k] = random.uniform(-100, 100)
        elif difficulty == "easy":
            for k in scores.keys():
                if scores[k] > -500:
                    scores[k] += random.uniform(-20, 20)

        if b_type == "spectator":
            scores["idle"] = 1000.0
            for k in scores.keys():
                if k != "idle":
                    scores[k] = -1000.0

        # Find highest score
        best_action = "idle"
        best_score = -9999.0

        for action in ["flee", "defend", "collect_booster", "attack", "chase", "use_skill", "kite", "flank", "idle"]:
            if scores[action] > best_score:
                best_score = scores[action]
                best_action = action

        # Fall back to personality behavior instead of returning personality name
        if best_action == "idle":
            return self.PERSONALITY_BEHAVIORS.get(personality, "idle")

        return best_action
