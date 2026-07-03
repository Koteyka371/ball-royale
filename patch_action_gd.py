import re

with open('src/ai/action.gd', 'r') as f:
    text = f.read()

search_quicksand_gd = """                        # Occasional slow debuff that lingers
                        var debuff_timer = 0.0
                        if self.ball.has_method("get_meta") and self.ball.has_meta("quicksand_debuff_timer"):
                            debuff_timer = self.ball.get_meta("quicksand_debuff_timer")
                        elif "quicksand_debuff_timer" in self.ball:
                            debuff_timer = self.ball.quicksand_debuff_timer

                        if debuff_timer <= 0.0:
                            if randf() < 0.1: # 10% chance per tick
                                debuff_timer = 2.0

                        if debuff_timer > 0.0:
                            debuff_timer -= delta
                            var base_speed = 100.0
                            if self.ball.has_method("get_meta") and self.ball.has_meta("base_speed"):
                                base_speed = self.ball.get_meta("base_speed")
                            elif "base_speed" in self.ball:
                                base_speed = self.ball.base_speed
                            self.ball.speed = base_speed * 0.3

                        if self.ball.has_method("set_meta"):
                            self.ball.set_meta("quicksand_debuff_timer", debuff_timer)
                            self.ball.set_meta("is_in_quicksand", true)
                        else:
                            self.ball.quicksand_debuff_timer = debuff_timer
                            self.ball.is_in_quicksand = true"""

replace_quicksand_gd = """                        var has_wt = false
                        var bt = ""
                        if "ball_type" in self.ball: bt = str(self.ball.ball_type).to_lower()
                        elif self.ball.has_method("get_meta") and self.ball.has_meta("ball_type"): bt = str(self.ball.get_meta("ball_type")).to_lower()
                        if "water" in bt or "swamp" in bt: has_wt = true
                        var tr = []
                        if "traits" in self.ball: tr = self.ball.traits
                        elif self.ball.has_method("get_meta") and self.ball.has_meta("traits"): tr = self.ball.get_meta("traits")
                        if typeof(tr) == TYPE_ARRAY:
                            for t in tr:
                                if "water" in str(t).to_lower() or "swamp" in str(t).to_lower():
                                    has_wt = true

                        # Occasional slow debuff that lingers
                        if not has_wt:
                            var debuff_timer = 0.0
                            if self.ball.has_method("get_meta") and self.ball.has_meta("quicksand_debuff_timer"):
                                debuff_timer = self.ball.get_meta("quicksand_debuff_timer")
                            elif "quicksand_debuff_timer" in self.ball:
                                debuff_timer = self.ball.quicksand_debuff_timer

                            if debuff_timer <= 0.0:
                                if randf() < 0.1: # 10% chance per tick
                                    debuff_timer = 2.0

                            if debuff_timer > 0.0:
                                debuff_timer -= delta
                                var base_speed = 100.0
                                if self.ball.has_method("get_meta") and self.ball.has_meta("base_speed"):
                                    base_speed = self.ball.get_meta("base_speed")
                                elif "base_speed" in self.ball:
                                    base_speed = self.ball.base_speed
                                self.ball.speed = base_speed * 0.3

                            if self.ball.has_method("set_meta"):
                                self.ball.set_meta("quicksand_debuff_timer", debuff_timer)
                            else:
                                self.ball.quicksand_debuff_timer = debuff_timer

                        if self.ball.has_method("set_meta"):
                            self.ball.set_meta("is_in_quicksand", true)
                        else:
                            self.ball.is_in_quicksand = true"""

if search_quicksand_gd in text:
    text = text.replace(search_quicksand_gd, replace_quicksand_gd)
    print("Replaced quicksand gd")
else:
    print("Could not find quicksand gd")

with open('src/ai/action.gd', 'w') as f:
    f.write(text)
