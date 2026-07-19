import re
import sys

def modify_action_gd():
    path = "src/ai/action.gd"
    with open(path, "r") as f:
        content = f.read()

    orig = """            elif "kind" in nearest and nearest.kind == "charging_shockwave_shield_booster":"""
    repl = """            elif "kind" in nearest and nearest.kind == "snow_globe_booster":
                if self.ball.has_method("set_meta"): self.ball.set_meta("freezing_immunity_timer", 15.0)
                else: self.ball.freezing_immunity_timer = 15.0
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1: self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1: self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "umbrella_booster":
                if self.ball.has_method("set_meta"): self.ball.set_meta("slippery_immunity_timer", 15.0)
                else: self.ball.slippery_immunity_timer = 15.0
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1: self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1: self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "charging_shockwave_shield_booster":"""

    content = content.replace(orig, repl)
    with open(path, "w") as f:
        f.write(content)

modify_action_gd()
