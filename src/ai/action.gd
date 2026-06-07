class_name ActionLayer
extends RefCounted

var ball = null
var world = null

func _init(ball_ref, world_ref):
    self.ball = ball_ref
    self.world = world_ref

func execute(strategy: String, delta: float):
    # Save the chosen strategy as current_action for testing/debugging
    if "current_action" in self.ball:
        self.ball.current_action = strategy

    if strategy == "flee":
        if self.ball.has_method("flee"):
            self.ball.flee(delta)
    elif strategy == "attack":
        if self.ball.has_method("attack"):
            self.ball.attack(delta)
    elif strategy == "defend":
        if self.ball.has_method("defend"):
            self.ball.defend(delta)
    elif strategy == "opportunistic" or strategy == "collect booster":
        if self.ball.has_method("collect_booster"):
            self.ball.collect_booster(delta)
    elif strategy == "use skill":
        if self.ball.has_method("use_skill"):
            self.ball.use_skill()
    elif strategy == "chase":
        if self.ball.has_method("chase"):
            self.ball.chase(delta)
        elif self.ball.has_method("attack"):
            self.ball.attack(delta)
    else:
        if self.ball.has_method("idle"):
            self.ball.idle(delta)
