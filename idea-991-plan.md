# Plan to implement Mutator: Gravity Reversal Pull

1. *Create the GravityReversalMutatorMode (GameMode)*
   - Append `GravityReversalMutatorMode` and add it to `GAME_MODES` in `src/ai/game_modes.py` and `src/ai/game_modes.gd`.
   - Tool call: `run_in_bash_session`
   - Command:
     ```bash
     cat << 'EOF_INNER' > patch_game_modes.py
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
EOF_INNER
     python3 patch_game_modes.py
     grep -rn "GravityReversalMutatorMode" src/ai/game_modes.py
     grep -rn "GravityReversalMutatorMode" src/ai/game_modes.gd
     ```

2. *Modify `Action.execute()` to invert pull strength when reversed*
   - Invert `pull_strength` in `action.py` and `action.gd`.
   - Tool call: `run_in_bash_session`
   - Command:
     ```bash
     cat << 'EOF_INNER' > patch_action.py
with open("src/ai/action.py", "r") as f:
    text = f.read()

text = text.replace("pull_strength = (hazard.radius * 2.0 * radius_mult / max(10.0, dist)) * 200.0 * delta\n                            nx, ny", "pull_strength = (hazard.radius * 2.0 * radius_mult / max(10.0, dist)) * 200.0 * delta\n                            if getattr(self.world, 'is_gravity_reversed', False): pull_strength *= -1.0\n                            nx, ny")
text = text.replace("pull_strength = (getattr(hazard, \"radius\", 150.0) * 3.0 / max(10.0, dist)) * 80.0 * delta\n                                self.ball.x", "pull_strength = (getattr(hazard, \"radius\", 150.0) * 3.0 / max(10.0, dist)) * 80.0 * delta\n                                if getattr(self.world, 'is_gravity_reversed', False): pull_strength *= -1.0\n                                self.ball.x")
text = text.replace("pull_strength = 200.0 * delta\n                                if isinstance(item, dict):", "pull_strength = 200.0 * delta\n                                if getattr(self.world, 'is_gravity_reversed', False): pull_strength *= -1.0\n                                if isinstance(item, dict):")
text = text.replace("pull_strength = 150.0 * delta\n                                if hasattr(hazard, \"x\"):", "pull_strength = 150.0 * delta\n                                if getattr(self.world, 'is_gravity_reversed', False): pull_strength *= -1.0\n                                if hasattr(hazard, \"x\"):")
text = text.replace("pull_strength = 100.0 * delta\n                                # Weak pull towards the center", "pull_strength = 100.0 * delta\n                                if getattr(self.world, 'is_gravity_reversed', False): pull_strength *= -1.0\n                                # Weak pull towards the center")
text = text.replace("pull_strength = 100.0 * delta\n                                if getattr(self.ball, \"anchor_booster_timer\", 0.0) <= 0:", "pull_strength = 100.0 * delta\n                                if getattr(self.world, 'is_gravity_reversed', False): pull_strength *= -1.0\n                                if getattr(self.ball, \"anchor_booster_timer\", 0.0) <= 0:")
text = text.replace("pull_strength = 300.0 * delta\n                dx = target.x", "pull_strength = 300.0 * delta\n                if getattr(self.world, 'is_gravity_reversed', False): pull_strength *= -1.0\n                dx = target.x")

with open("src/ai/action.py", "w") as f:
    f.write(text)

with open("src/ai/action.gd", "r") as f:
    gd_text = f.read()

gd_text = gd_text.replace("pull_strength = (hazard.radius * 2.0 * radius_mult / max(10.0, dist)) * 200.0 * delta\n\t\t\t\t\t\t\tvar nx = dx / max(0.1, dist)", "pull_strength = (hazard.radius * 2.0 * radius_mult / max(10.0, dist)) * 200.0 * delta\n\t\t\t\t\t\t\tif typeof(self.world) == TYPE_DICTIONARY and self.world.get(\"is_gravity_reversed\", false):\n\t\t\t\t\t\t\t\tpull_strength *= -1.0\n\t\t\t\t\t\t\telif typeof(self.world) != TYPE_DICTIONARY and \"is_gravity_reversed\" in self.world and self.world.is_gravity_reversed:\n\t\t\t\t\t\t\t\tpull_strength *= -1.0\n\t\t\t\t\t\t\tvar nx = dx / max(0.1, dist)")

with open("src/ai/action.gd", "w") as f:
    f.write(gd_text)
EOF_INNER
     python3 patch_action.py
     grep -rn "is_gravity_reversed" src/ai/action.py
     ```

3. *Modify Specific Game Modes (game_modes.py and game_modes.gd)*
   - Modify specific `pull_strength` and `push_strength` references in `game_modes.py` and `.gd`.
   - Tool call: `run_in_bash_session`
   - Command:
     ```bash
     cat << 'EOF_INNER' > patch_game_modes2.py
with open("src/ai/game_modes.py", "r") as f:
    text = f.read()

text = text.replace("pull_strength = min(pull_strength, 150.0 * radius_multiplier)\n\n                    b.x", "pull_strength = min(pull_strength, 150.0 * radius_multiplier)\n                    if getattr(world, 'is_gravity_reversed', False): pull_strength *= -1.0\n\n                    b.x")
text = text.replace("b.vx += (dx / dist) * self.pull_strength * delta", "mod_pull = -self.pull_strength if getattr(world, 'is_gravity_reversed', False) else self.pull_strength\n                    b.vx += (dx / dist) * mod_pull * delta")
text = text.replace("b.vy += (dy / dist) * self.pull_strength * delta", "b.vy += (dy / dist) * mod_pull * delta")
text = text.replace("push_strength = 2000.0 * (1.0 - min(1.0, dist / self.max_danger_radius)) # Stronger push closer to center\n                    if not hasattr(b, \"vx\"):", "push_strength = 2000.0 * (1.0 - min(1.0, dist / self.max_danger_radius))\n                    if getattr(world, 'is_gravity_reversed', False): push_strength *= -1.0\n                    if not hasattr(b, \"vx\"):")

with open("src/ai/game_modes.py", "w") as f:
    f.write(text)

with open("src/ai/game_modes.gd", "r") as f:
    gd_text = f.read()

gd_text = gd_text.replace("pull_strength = min(pull_strength, 150.0 * radius_multiplier)\n\n\t\t\t\t\tif typeof(b) == TYPE_DICTIONARY:", "pull_strength = min(pull_strength, 150.0 * radius_multiplier)\n\t\t\t\t\tvar is_rev = false\n\t\t\t\t\tif typeof(world) == TYPE_DICTIONARY:\n\t\t\t\t\t\tis_rev = world.get(\"is_gravity_reversed\", false)\n\t\t\t\t\telse:\n\t\t\t\t\t\tis_rev = world.is_gravity_reversed if \"is_gravity_reversed\" in world else false\n\t\t\t\t\tif is_rev: pull_strength *= -1.0\n\n\t\t\t\t\tif typeof(b) == TYPE_DICTIONARY:")
gd_text = gd_text.replace("push_strength = 2000.0 * (1.0 - min(1.0, dist / max_danger_radius))\n\t\t\t\t\tif typeof(b) == TYPE_DICTIONARY:", "push_strength = 2000.0 * (1.0 - min(1.0, dist / max_danger_radius))\n\t\t\t\t\tvar is_rev = false\n\t\t\t\t\tif typeof(world) == TYPE_DICTIONARY:\n\t\t\t\t\t\tis_rev = world.get(\"is_gravity_reversed\", false)\n\t\t\t\t\telse:\n\t\t\t\t\t\tis_rev = world.is_gravity_reversed if \"is_gravity_reversed\" in world else false\n\t\t\t\t\tif is_rev: push_strength *= -1.0\n\t\t\t\t\tif typeof(b) == TYPE_DICTIONARY:")

with open("src/ai/game_modes.gd", "w") as f:
    f.write(gd_text)
EOF_INNER
     python3 patch_game_modes2.py
     grep -rn "is_gravity_reversed" src/ai/game_modes.py
     ```

4. *Add tests*
   - Write test to `src/ai/test_gravity_reversal_mutator.py`.
   - Tool call: `run_in_bash_session`
   - Command:
     ```bash
     cat << 'EOF_INNER' > src/ai/test_gravity_reversal_mutator.py
from ai.game_modes import GAME_MODES, GravityReversalMutatorMode, BlackHoleMode

class MockWorld:
    def __init__(self):
        self.arena = type("Arena", (), {"width": 1000, "height": 1000, "hazards": []})
        self.events = []
        self.is_gravity_reversed = False
        self.dead_balls = []

    def add_event(self, kind, data):
        self.events.append((kind, data))

def test_gravity_reversal_mutator_toggles_state():
    world = MockWorld()
    mode = GravityReversalMutatorMode()
    assert mode.is_gravity_reversed == False
    assert world.is_gravity_reversed == False
    mode.tick(world, [], delta=10.1)
    assert mode.is_gravity_reversed == True
    assert world.is_gravity_reversed == True
    mode.tick(world, [], delta=10.1)
    assert mode.is_gravity_reversed == False
    assert world.is_gravity_reversed == False

def test_blackhole_repels_when_reversed():
    world = MockWorld()
    world.is_gravity_reversed = True
    bh_mode = BlackHoleMode()
    bh_mode.black_hole_radius = 50.0
    class MockBall:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.alive = True
            self.ball_type = "player"
            self.weather_immunity_timer = 0.0
    b = MockBall(500, 400)
    balls = [b]
    import math
    initial_dist = math.hypot(500 - b.x, 500 - b.y)
    bh_mode.tick(world, balls, delta=0.1)
    new_dist = math.hypot(500 - b.x, 500 - b.y)
    assert new_dist > initial_dist
EOF_INNER
     ```

5. *Run tests*
   - Execute the tests.
   - Tool call: `run_in_bash_session`
   - Command:
     ```bash
     PYTHONPATH=src pytest
     ```

6. *Complete pre commit steps*
   - Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.

7. *Ideas Inbox & Submit*
   - Create 2 ideas in the `ideas/` directory and submit using the exact CLI tool.
   - Tool call: `submit`
   - Command:
     ```json
     {
       "branch_name": "idea-991",
       "commit_message": "Add gravity reversal mutator",
       "title": "[idea-991] Add Gravity Reversal Mutator",
       "description": "Task: idea-991"
     }
     ```
