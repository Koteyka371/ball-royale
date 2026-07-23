import re

file_path = "src/ai/action.gd"
with open(file_path, "r") as f:
    content = f.read()

pullable_re = r'var pullable = \["event_horizon_trap", "repulsion_zone"'
pullable_replacement = 'var pullable = ["deployable_proximity_mud_puddle", "event_horizon_trap", "repulsion_zone"'
content = re.sub(pullable_re, pullable_replacement, content)

pickup_logic = """            elif "kind" in nearest and nearest.kind == "deployable_mud_puddle":
                var b_inv = []
                if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("get_meta"):
                    if self.ball.has_meta("inventory"): b_inv = self.ball.get_meta("inventory")
                elif "inventory" in self.ball: b_inv = self.ball.inventory
                b_inv.append("deployable_mud_puddle")
                if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"): self.ball.set_meta("inventory", b_inv)
                elif "inventory" in self.ball: self.ball.inventory = b_inv

                if world != null and "arena" in world and "hazards" in world.arena:
                    var idx = world.arena.hazards.find(nearest)
                    if idx != -1:
                        world.arena.hazards.remove_at(idx)"""

new_pickup_logic = pickup_logic + """
            elif "kind" in nearest and nearest.kind == "deployable_proximity_mud_puddle":
                var b_inv = []
                if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("get_meta"):
                    if self.ball.has_meta("inventory"): b_inv = self.ball.get_meta("inventory")
                elif "inventory" in self.ball: b_inv = self.ball.inventory
                b_inv.append("deployable_proximity_mud_puddle")
                if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"): self.ball.set_meta("inventory", b_inv)
                elif "inventory" in self.ball: self.ball.inventory = b_inv

                if world != null and "arena" in world and "hazards" in world.arena:
                    var idx = world.arena.hazards.find(nearest)
                    if idx != -1:
                        world.arena.hazards.remove_at(idx)"""

content = content.replace(pickup_logic, new_pickup_logic)

with open(file_path, "w") as f:
    f.write(content)
