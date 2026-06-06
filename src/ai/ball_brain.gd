class_name BallBrain
extends Node

const Perception = preload("res://src/ai/perception.gd")

# Reference to the ball this brain controls
var ball = null
var world = null
var perception_layer = null

func _init(ball_ref, world_ref):
    self.ball = ball_ref
    self.world = world_ref
    self.perception_layer = Perception.new(self.ball, self.world)

# Main processing loop
func process(delta):
    var perception_data = perception()
    var emotion_state = emotion(perception_data)
    var decision = decision(perception_data, emotion_state)
    action(decision, delta)

# 1. PERCEPTION LAYER
# Scans environment for entities via Perception layer
func perception() -> Dictionary:
    return self.perception_layer.scan()

# 2. EMOTION LAYER
# Determines current emotional state based on HP and situation
func emotion(perception_data: Dictionary) -> String:
    var hp_percent = 1.0
    if self.ball.has_method("get_hp_percent"):
        hp_percent = self.ball.get_hp_percent()
    elif "hp" in self.ball and "max_hp" in self.ball:
        hp_percent = float(self.ball.hp) / float(self.ball.max_hp)

    if hp_percent < 0.3:
        return "fear"

    if perception_data["boosters"].size() > 0:
        return "greed"

    if hp_percent > 0.8 and perception_data["enemies"].size() > 0:
        return "rage"

    return "neutral"

# 3. DECISION LAYER
# Chooses strategy based on perception and emotion
func decision(perception_data: Dictionary, emotion_state: String) -> String:
    var hp_percent = 1.0
    if self.ball.has_method("get_hp_percent"):
        hp_percent = self.ball.get_hp_percent()
    elif "hp" in self.ball and "max_hp" in self.ball:
        hp_percent = float(self.ball.hp) / float(self.ball.max_hp)

    # Decision logic based on game design
    if hp_percent < 0.3 or emotion_state == "fear":
        return "flee"

    if perception_data["danger_level"] > 0.7:
        return "defend"

    if perception_data["opportunity_level"] > 0.5 or emotion_state == "greed":
        if perception_data["boosters"].size() > 0:
            return "opportunistic"

    if perception_data["enemies"].size() > 0:
        return "attack"

    # Default behavior depends on personality (fallback to idle if none)
    var personality = "idle"
    if "personality" in self.ball:
        personality = self.ball.personality

    return personality

# 4. ACTION LAYER
# Executes chosen strategy
func action(strategy: String, delta: float):
    # Depending on strategy, call the appropriate behavior on the ball
    if strategy == "flee":
        if self.ball.has_method("flee"):
            self.ball.flee(delta)
    elif strategy == "attack":
        if self.ball.has_method("attack"):
            self.ball.attack(delta)
    elif strategy == "defend":
        if self.ball.has_method("defend"):
            self.ball.defend(delta)
    elif strategy == "opportunistic":
        if self.ball.has_method("collect_booster"):
            self.ball.collect_booster(delta)
    else:
        if self.ball.has_method("idle"):
            self.ball.idle(delta)
