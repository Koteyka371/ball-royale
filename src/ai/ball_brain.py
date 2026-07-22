import random
from typing import Any, Dict

from .perception import Perception
from .emotion import Emotion
from .decision import Decision
from .action import Action


class BallBrain:
    """
    Core AI system for balls.
    Processes information through 4 layers: Perception, Emotion, Decision, Action.
    """

    def __init__(self, ball: Any, world: Any):
        self.ball = ball
        self.world = world

        # Apply profile bonuses directly to the ball's stats upon creation
        try:
            from system.profile import ProfileManager
            pm = ProfileManager("profile.json")
            if "bonus_hp" in pm.data.get("bonuses", {}):
                hp_percent = self.ball.hp / self.ball.max_hp if self.ball.max_hp > 0 else 1.0
                self.ball.max_hp += pm.data["bonuses"]["bonus_hp"] * 10
                self.ball.hp = self.ball.max_hp * hp_percent
            if "bonus_speed" in pm.data.get("bonuses", {}):
                self.ball.speed += pm.data["bonuses"]["bonus_speed"] * 5
            if "bonus_damage" in pm.data.get("bonuses", {}):
                self.ball.damage += pm.data["bonuses"]["bonus_damage"] * 2

            # Apply guild buffs
            if pm.data.get("guild_name", ""):
                try:
                    from system.guild import GuildManager
                    gm = GuildManager("guilds.json")
                    guild_buffs = gm.get_guild_buffs(pm.data["guild_name"])
                    guild_perks = gm.get_guild_perks(pm.data["guild_name"])

                    hp_multi = 1.0
                    speed_multi = 1.0
                    dmg_multi = 1.0

                    for perk in guild_perks:
                        if perk == "hp_5_percent": hp_multi += 0.05
                        elif perk == "hp_10_percent": hp_multi += 0.10
                        elif perk == "speed_5_percent": speed_multi += 0.05
                        elif perk == "speed_10_percent": speed_multi += 0.10
                        elif perk == "dmg_5_percent": dmg_multi += 0.05
                        elif perk == "dmg_10_percent": dmg_multi += 0.10
                        elif perk == "hp_15_percent": hp_multi += 0.15
                        elif perk == "speed_15_percent": speed_multi += 0.15
                        elif perk == "dmg_15_percent": dmg_multi += 0.15
                        elif perk == "materials_drop_rate_10_percent": self.ball.materials_drop_rate = getattr(self.ball, 'materials_drop_rate', 1.0) + 0.10
                        elif perk == "materials_drop_rate_20_percent": self.ball.materials_drop_rate = getattr(self.ball, 'materials_drop_rate', 1.0) + 0.20

                    if guild_buffs or guild_perks:
                        hp_percent = self.ball.hp / self.ball.max_hp if getattr(self.ball, 'max_hp', 0) > 0 else 1.0
                        if hasattr(self.ball, 'max_hp'):
                            self.ball.max_hp += guild_buffs.get("bonus_hp", 0) * 10
                            self.ball.max_hp *= hp_multi
                        if hasattr(self.ball, 'hp'):
                            self.ball.hp = self.ball.max_hp * hp_percent
                        if hasattr(self.ball, 'speed'):
                            self.ball.speed += guild_buffs.get("bonus_speed", 0) * 5
                            self.ball.speed *= speed_multi
                        if hasattr(self.ball, 'damage'):
                            self.ball.damage += guild_buffs.get("bonus_damage", 0) * 2
                            self.ball.damage *= dmg_multi
                except Exception:
                    pass


            # Apply prestige upgrades (from prestige tokens)
            prestige_upgrades = pm.data.get("prestige_upgrades", {})
            if "permanent_hp" in prestige_upgrades:
                bonus = prestige_upgrades["permanent_hp"] * 10
                hp_percent = self.ball.hp / self.ball.max_hp if getattr(self.ball, 'max_hp', 0) > 0 else 1.0
                if hasattr(self.ball, 'max_hp'):
                    self.ball.max_hp += bonus
                if hasattr(self.ball, 'hp'):
                    self.ball.hp = self.ball.max_hp * hp_percent
            if "permanent_speed" in prestige_upgrades:
                if hasattr(self.ball, 'speed'):
                    self.ball.speed += prestige_upgrades["permanent_speed"] * 5
            if "permanent_damage" in prestige_upgrades:
                if hasattr(self.ball, 'damage'):
                    self.ball.damage += prestige_upgrades["permanent_damage"] * 2


            # Apply starting artifacts
            if "starting_artifact_shield" in prestige_upgrades:
                if not hasattr(self.ball, 'inventory'):
                    self.ball.inventory = []
                self.ball.inventory.append("shield")
            if "starting_artifact_dash" in prestige_upgrades:
                if not hasattr(self.ball, 'inventory'):
                    self.ball.inventory = []
                self.ball.inventory.append("dash")
            if isinstance(prestige_upgrades, dict) and "shield_capacity_up" in prestige_upgrades:
                self.ball.bonus_reflect_shield_capacity = prestige_upgrades["shield_capacity_up"] * 20.0
            if isinstance(prestige_upgrades, dict) and "shield_duration_up" in prestige_upgrades:
                self.ball.bonus_reflect_shield_duration = prestige_upgrades["shield_duration_up"] * 1.0

            # Apply prestige aura and permanent stat increase
            prestige_level = pm.data.get("prestige_level", 0)
            if prestige_level > 0:
                self.ball.has_aura = True
                stat_multiplier = 1.0 + (0.05 * prestige_level)

                hp_percent = self.ball.hp / self.ball.max_hp if getattr(self.ball, 'max_hp', 0) > 0 else 1.0
                if hasattr(self.ball, 'max_hp'):
                    self.ball.max_hp *= stat_multiplier
                if hasattr(self.ball, 'hp'):
                    self.ball.hp = self.ball.max_hp * hp_percent
                if hasattr(self.ball, 'speed'):
                    self.ball.speed *= stat_multiplier
                if hasattr(self.ball, 'damage'):
                    self.ball.damage *= stat_multiplier
        except Exception:
            # print(f"Error applying profile bonuses: {e}")
            pass
                # Apply skin-based passive perks
        skin = getattr(self.ball, "skin", "default")

        # Determine current weather if possible to apply skin-specific weather buffs
        current_weather = "clear"
        if hasattr(self, "world"):
            if getattr(self.world, "game_mode", None) and hasattr(self.world.game_mode, "weather"):
                current_weather = self.world.game_mode.weather
            elif getattr(self.world, "arena", None) and hasattr(self.world.arena, "weather"):
                current_weather = self.world.arena.weather

        # Snow tires cosmetic buff globally during snow/blizzard weather
        if skin == "snow_tires" and current_weather in ["snow", "blizzard"]:
            self.ball.speed = getattr(self.ball, "speed", 100.0) * 1.25
            self.ball.status_resistance = getattr(self.ball, "status_resistance", 0.0) + 0.30

        if skin == "veteran":
            self.ball.status_resistance = getattr(self.ball, "status_resistance", 0.0) + 0.02
        elif skin == "legendary":
            self.ball.has_aura = True
        elif skin == "elite":
            self.ball.speed = getattr(self.ball, "speed", 100.0) * 1.05
        elif skin == "prestige_master":
            self.ball.has_aura = True
            self.ball.speed = getattr(self.ball, "speed", 100.0) * 1.08
            self.ball.status_resistance = getattr(self.ball, "status_resistance", 0.0) + 0.05
        elif skin == "prestige_grandmaster":
            self.ball.has_aura = True
            self.ball.speed = getattr(self.ball, "speed", 100.0) * 1.15
            self.ball.status_resistance = getattr(self.ball, "status_resistance", 0.0) + 0.10
            self.ball.damage = getattr(self.ball, "damage", 10.0) * 1.10
        elif skin.startswith("prestige_skin_"):
            try:
                level = int(skin.split("_")[2])
                self.ball.has_aura = True
                self.ball.speed = getattr(self.ball, "speed", 100.0) * (1.0 + level * 0.015)
                self.ball.status_resistance = getattr(self.ball, "status_resistance", 0.0) + (level * 0.01)
                self.ball.damage = getattr(self.ball, "damage", 10.0) * (1.0 + level * 0.01)
            except ValueError:
                pass

        self.perception_layer = Perception(self.ball, self.world)

        self.emotion_layer = Emotion(self.ball, self.world)
        self.decision_layer = Decision(self.ball, self.world)
        self.action_layer = Action(self.ball, self.world)

        self._reaction_timer = 0.0
        self._current_decision = "idle"

    def process(self, delta: float) -> None:
        """Main processing loop through the 4 layers."""
        self._reaction_timer -= delta

        if self._reaction_timer <= 0:
            perception_data = self.perception()
            emotion_state = self.emotion(perception_data)

            self.ball.emotion = emotion_state

            decision = self.decision(perception_data, emotion_state)

            self._current_decision = decision

            difficulty = getattr(self.ball, "difficulty", "medium")
            if difficulty == "easy":
                self._reaction_timer = 0.5
            elif difficulty == "medium":
                self._reaction_timer = 0.1
            elif difficulty == "hard":
                self._reaction_timer = 0.0
            elif difficulty == "chaos":
                self._reaction_timer = random.uniform(0.0, 0.2)
            else:
                self._reaction_timer = 0.1

        self.action(self._current_decision, delta)

    def perception(self) -> Dict[str, Any]:
        """
        1. PERCEPTION LAYER
        Delegates scanning the environment to the Perception class.
        """
        return self.perception_layer.scan()

    def emotion(self, perception_data: Dict[str, Any]) -> str:
        """
        2. EMOTION LAYER
        Delegates determining current emotional state to the Emotion class.
        """
        return self.emotion_layer.get_state(perception_data)

    def decision(self, perception_data: Dict[str, Any], emotion_state: str) -> str:
        """
        3. DECISION LAYER
        Chooses strategy based on perception and emotion.
        """
        return self.decision_layer.choose_action(perception_data, emotion_state)

    def action(self, strategy: str, delta: float) -> None:
        """
        4. ACTION LAYER
        Delegates executing chosen strategy to the Action class.
        """
        self.action_layer.execute(strategy, delta)
