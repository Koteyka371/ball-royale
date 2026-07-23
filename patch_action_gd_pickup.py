import re

with open("src/ai/action.gd", "r") as f:
    text = f.read()

pickup_code = """
            elif "kind" in nearest and nearest.kind == "deployable_acid_puddle":
                var b_inv = []
                if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("get_meta"):
                    if self.ball.has_meta("inventory"): b_inv = self.ball.get_meta("inventory")
                elif "inventory" in self.ball: b_inv = self.ball.inventory
                b_inv.append("deployable_acid_puddle")
                if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"): self.ball.set_meta("inventory", b_inv)
                elif "inventory" in self.ball: self.ball.inventory = b_inv

                if world != null and "arena" in world and "hazards" in world.arena:
                    var idx = world.arena.hazards.find(nearest)
                    if idx != -1:
                        world.arena.hazards.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "deployable_shockwave_mine":
                var b_inv = []
                if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("get_meta"):
                    if self.ball.has_meta("inventory"): b_inv = self.ball.get_meta("inventory")
                elif "inventory" in self.ball: b_inv = self.ball.inventory
                b_inv.append("deployable_shockwave_mine")
                if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"): self.ball.set_meta("inventory", b_inv)
                elif "inventory" in self.ball: self.ball.inventory = b_inv

                if world != null and "arena" in world and "hazards" in world.arena:
                    var idx = world.arena.hazards.find(nearest)
                    if idx != -1:
                        world.arena.hazards.remove_at(idx)
"""

text = re.sub(r'\s+elif "kind" in nearest and nearest\.kind == "deployable_acid_puddle":\s+var b_inv = \[\]\s+if typeof\(self\.ball\) == TYPE_OBJECT and self\.ball\.has_method\("get_meta"\):\s+if self\.ball\.has_meta\("inventory"\): b_inv = self\.ball\.get_meta\("inventory"\)\s+elif "inventory" in self\.ball: b_inv = self\.ball\.inventory\s+b_inv\.append\("deployable_acid_puddle"\)\s+if typeof\(self\.ball\) == TYPE_OBJECT and self\.ball\.has_method\("set_meta"\): self\.ball\.set_meta\("inventory", b_inv\)\s+elif "inventory" in self\.ball: self\.ball\.inventory = b_inv\s+if world != null and "arena" in world and "hazards" in world\.arena:\s+var idx = world\.arena\.hazards\.find\(nearest\)\s+if idx != -1:\s+world\.arena\.hazards\.remove_at\(idx\)', pickup_code, text, count=1, flags=re.DOTALL)

text = text.replace('"position_swap_booster", "portal_gun_item"', '"position_swap_booster", "deployable_shockwave_mine", "shockwave_mine", "portal_gun_item"')
text = text.replace('"position_swap_booster", "magnet_booster"', '"position_swap_booster", "deployable_shockwave_mine", "shockwave_mine", "magnet_booster"')
text = text.replace('"position_swap_booster", "nemesis_booster"', '"position_swap_booster", "deployable_shockwave_mine", "shockwave_mine", "nemesis_booster"')


with open("src/ai/action.gd", "w") as f:
    f.write(text)
