import re

py_code = """
class GravityReversalMutatorMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Gravity Reversal Mutator"
        self.description = "A mutator that intermittently reverses the gravitational pull of hazards and game modes."
        self.gravity_reverse_timer = 0.0
        self.is_gravity_reversed = False

    def tick(self, world, balls, delta=0.016):
        super().tick(world, balls, delta)
        self.gravity_reverse_timer -= delta
        if self.gravity_reverse_timer <= 0:
            self.gravity_reverse_timer = 10.0
            self.is_gravity_reversed = not self.is_gravity_reversed
            setattr(world, "is_gravity_reversed", self.is_gravity_reversed)
            if hasattr(world, "add_event"):
                world.add_event("gravity_reversal_state_change", {"active": self.is_gravity_reversed})
"""
gd_code = """
class GravityReversalMutatorMode extends GameMode:
	var gravity_reverse_timer: float = 0.0
	var is_gravity_reversed: bool = false

	func _init() -> void:
		name = "Gravity Reversal Mutator"
		description = "A mutator that intermittently reverses the gravitational pull of hazards and game modes."

	func tick(world, balls: Array, delta: float = 0.016) -> void:
		super.tick(world, balls, delta)
		gravity_reverse_timer -= delta
		if gravity_reverse_timer <= 0:
			gravity_reverse_timer = 10.0
			is_gravity_reversed = not is_gravity_reversed
			if typeof(world) == TYPE_DICTIONARY:
				world["is_gravity_reversed"] = is_gravity_reversed
			else:
				world.is_gravity_reversed = is_gravity_reversed
			if typeof(world) != TYPE_DICTIONARY and world.has_method("add_event"):
				world.add_event("gravity_reversal_state_change", {"active": is_gravity_reversed})
"""

with open("src/ai/game_modes.py", "r") as f:
    py_text = f.read()
if "class GravityReversalMutatorMode" not in py_text:
    py_text = py_text.replace("GAME_MODES = {", py_code + "\nGAME_MODES = {")
    py_text = py_text.replace('    "reverse_gravity_event": ReverseGravityEventMode(),', '    "reverse_gravity_event": ReverseGravityEventMode(),\n    "gravity_reversal_mutator": GravityReversalMutatorMode(),')
with open("src/ai/game_modes.py", "w") as f:
    f.write(py_text)

with open("src/ai/game_modes.gd", "r") as f:
    gd_text = f.read()
if "class GravityReversalMutatorMode" not in gd_text:
    gd_text = gd_text.replace("var GAME_MODES = {", gd_code + "\nvar GAME_MODES = {")
    gd_text = gd_text.replace('	"reverse_gravity_event": ReverseGravityEventMode.new(),', '	"reverse_gravity_event": ReverseGravityEventMode.new(),\n	"gravity_reversal_mutator": GravityReversalMutatorMode.new(),')
with open("src/ai/game_modes.gd", "w") as f:
    f.write(gd_text)
