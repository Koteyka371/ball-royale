class_name BallBrain
extends Node

const Perception = preload("res://src/ai/perception.gd")
const EmotionLayer = preload("res://src/ai/emotion.gd")
const DecisionLayer = preload("res://src/ai/decision.gd")
const ActionLayer = preload("res://src/ai/action.gd")

# Reference to the ball this brain controls
var ball = null
var world = null
var perception_layer = null
var emotion_layer = null
var decision_layer = null
var action_layer = null

var _reaction_timer = 0.0
var _current_decision = "idle"

func _init(ball_ref, world_ref):
    self.ball = ball_ref
    self.world = world_ref

    var pm = ProfileManager.new()
    if "bonus_hp" in pm.data.get("bonuses", {}):
        if "max_hp" in self.ball:
            self.ball.max_hp += pm.data["bonuses"]["bonus_hp"] * 10
            self.ball.hp = self.ball.max_hp
    if "bonus_speed" in pm.data.get("bonuses", {}):
        if "speed" in self.ball:
            self.ball.speed += pm.data["bonuses"]["bonus_speed"] * 5
    if "bonus_damage" in pm.data.get("bonuses", {}):
        if "damage" in self.ball:
            self.ball.damage += pm.data["bonuses"]["bonus_damage"] * 2

    # Apply guild buffs
    if pm.data.has("guild_name") and pm.data["guild_name"] != "":
        var gm = load("res://src/system/guild.gd").new()
        var guild_buffs = gm.get_guild_buffs(pm.data["guild_name"])
        if guild_buffs.size() > 0:
            if "max_hp" in self.ball:
                var hp_percent = 1.0
                if self.ball.max_hp > 0:
                    hp_percent = float(self.ball.hp) / float(self.ball.max_hp)
                self.ball.max_hp += guild_buffs.get("bonus_hp", 0) * 10
                self.ball.hp = self.ball.max_hp * hp_percent
            if "speed" in self.ball:
                self.ball.speed += guild_buffs.get("bonus_speed", 0) * 5
            if "damage" in self.ball:
                self.ball.damage += guild_buffs.get("bonus_damage", 0) * 2

    # Apply prestige upgrades (from prestige tokens)
    var prestige_upgrades = pm.data.get("prestige_upgrades", {})
    if "permanent_hp" in prestige_upgrades:
        var bonus = prestige_upgrades["permanent_hp"] * 10
        if "max_hp" in self.ball:
            var hp_percent = 1.0
            if self.ball.max_hp > 0:
                hp_percent = float(self.ball.hp) / float(self.ball.max_hp)
            self.ball.max_hp += bonus
            self.ball.hp = self.ball.max_hp * hp_percent
    if "permanent_speed" in prestige_upgrades:
        if "speed" in self.ball:
            self.ball.speed += prestige_upgrades["permanent_speed"] * 5
    if "permanent_damage" in prestige_upgrades:
        if "damage" in self.ball:
            self.ball.damage += prestige_upgrades["permanent_damage"] * 2


    # Apply starting artifacts
    if "starting_artifact_shield" in prestige_upgrades:
        if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("get_meta"):
            var inv = []
            if self.ball.has_meta("inventory"):
                inv = self.ball.get_meta("inventory")
            inv.append("shield")
            self.ball.set_meta("inventory", inv)
        elif "inventory" in self.ball:
            self.ball.inventory.append("shield")
    if "starting_artifact_dash" in prestige_upgrades:
        if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("get_meta"):
            var inv = []
            if self.ball.has_meta("inventory"):
                inv = self.ball.get_meta("inventory")
            inv.append("dash")
            self.ball.set_meta("inventory", inv)
        elif "inventory" in self.ball:
            self.ball.inventory.append("dash")

    var prestige_level = pm.data.get("prestige_level", 0)
    if prestige_level > 0:
        if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"):
            self.ball.set_meta("has_aura", true)
        elif "has_aura" in self.ball:
            self.ball.has_aura = true
        var stat_multiplier = 1.0 + (0.05 * prestige_level)
        if "max_hp" in self.ball:
            var hp_percent = 1.0
            if self.ball.max_hp > 0:
                hp_percent = float(self.ball.hp) / float(self.ball.max_hp)
            self.ball.max_hp *= stat_multiplier
            self.ball.hp = self.ball.max_hp * hp_percent
        if "speed" in self.ball:
            self.ball.speed *= stat_multiplier
        if "damage" in self.ball:
            self.ball.damage *= stat_multiplier
    # Apply skin-based passive perks
    var skin = "default"
    if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("get_meta"):
        if self.ball.has_meta("skin"):
            skin = self.ball.get_meta("skin")
        elif "skin" in self.ball:
            skin = self.ball.skin
    elif "skin" in self.ball:
        skin = self.ball.skin

    if skin == "veteran":
        var current_res = 0.0
        if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("get_meta") and self.ball.has_meta("status_resistance"):
            current_res = self.ball.get_meta("status_resistance")
        elif "status_resistance" in self.ball:
            current_res = self.ball.status_resistance

        if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"):
            self.ball.set_meta("status_resistance", current_res + 0.02)
        elif "status_resistance" in self.ball:
            self.ball.status_resistance = current_res + 0.02
    elif skin == "legendary":
        if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"):
            self.ball.set_meta("has_aura", true)
        elif "has_aura" in self.ball:
            self.ball.has_aura = true
    elif skin == "elite":
        var current_speed = 100.0
        if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("get_meta") and self.ball.has_meta("speed"):
            current_speed = self.ball.get_meta("speed")
        elif "speed" in self.ball:
            current_speed = self.ball.speed

        if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"):
            self.ball.set_meta("speed", current_speed * 1.05)
        elif "speed" in self.ball:
            self.ball.speed = current_speed * 1.05
    elif skin == "prestige_master":
        if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"):
            self.ball.set_meta("has_aura", true)
            var current_speed = self.ball.get_meta("speed") if self.ball.has_meta("speed") else 100.0
            self.ball.set_meta("speed", current_speed * 1.08)
            var current_res = self.ball.get_meta("status_resistance") if self.ball.has_meta("status_resistance") else 0.0
            self.ball.set_meta("status_resistance", current_res + 0.05)
        else:
            if "has_aura" in self.ball: self.ball.has_aura = true
            if "speed" in self.ball: self.ball.speed = self.ball.speed * 1.08
            if "status_resistance" in self.ball: self.ball.status_resistance = self.ball.status_resistance + 0.05
    elif skin == "prestige_grandmaster":
        if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"):
            self.ball.set_meta("has_aura", true)
            var current_speed = self.ball.get_meta("speed") if self.ball.has_meta("speed") else 100.0
            self.ball.set_meta("speed", current_speed * 1.15)
            var current_res = self.ball.get_meta("status_resistance") if self.ball.has_meta("status_resistance") else 0.0
            self.ball.set_meta("status_resistance", current_res + 0.10)
            var current_dmg = self.ball.get_meta("damage") if self.ball.has_meta("damage") else 10.0
            self.ball.set_meta("damage", current_dmg * 1.10)
        else:
            if "has_aura" in self.ball: self.ball.has_aura = true
            if "speed" in self.ball: self.ball.speed = self.ball.speed * 1.15
            if "status_resistance" in self.ball: self.ball.status_resistance = self.ball.status_resistance + 0.10
            if "damage" in self.ball: self.ball.damage = self.ball.damage * 1.10

    self.perception_layer = Perception.new(self.ball, self.world)

    self.emotion_layer = EmotionLayer.new(self.ball, self.world)
    self.decision_layer = DecisionLayer.new(self.ball, self.world)
    self.action_layer = ActionLayer.new(self.ball, self.world)

# Main processing loop
func process(delta):
    self._reaction_timer -= delta

    if self._reaction_timer <= 0:
        var perception_data = perception()
        var emotion_state = emotion(perception_data)

        if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"):
            self.ball.set_meta("emotion", emotion_state)
        elif "emotion" in self.ball:
            self.ball.emotion = emotion_state

        var decision_str = decision(perception_data, emotion_state)
        self._current_decision = decision_str

        var difficulty = "medium"
        if "difficulty" in self.ball:
            difficulty = self.ball.difficulty

        if difficulty == "easy":
            self._reaction_timer = 0.5
        elif difficulty == "medium":
            self._reaction_timer = 0.1
        elif difficulty == "hard":
            self._reaction_timer = 0.0
        elif difficulty == "chaos":
            self._reaction_timer = randf_range(0.0, 0.2)
        else:
            self._reaction_timer = 0.1

    action(self._current_decision, delta)

# 1. PERCEPTION LAYER
# Scans environment for entities via Perception layer
func perception() -> Dictionary:
    return self.perception_layer.scan()

# 2. EMOTION LAYER
# Delegates determining current emotional state to the Emotion class.
func emotion(perception_data: Dictionary) -> String:
    return self.emotion_layer.get_state(perception_data)

# 3. DECISION LAYER
# Chooses strategy based on perception and emotion
func decision(perception_data: Dictionary, emotion_state: String) -> String:
    return self.decision_layer.choose_action(perception_data, emotion_state)

# 4. ACTION LAYER
# Delegates executing chosen strategy to the ActionLayer
func action(strategy: String, delta: float):
    self.action_layer.execute(strategy, delta)
