with open("src/ai/action.gd", "r") as f:
    lines = f.readlines()

insert_idx = -1
for i, line in enumerate(lines):
    if "func execute(strategy, delta=1.0):" in line:
        insert_idx = i + 1
        break

lines.insert(insert_idx, """
    # Decrement wet_debuff_timer and restore speed
    var wet_timer = 0.0
    if typeof(self.ball) == TYPE_DICTIONARY:
        if self.ball.has("wet_debuff_timer"):
            wet_timer = self.ball["wet_debuff_timer"]
    else:
        if "wet_debuff_timer" in self.ball:
            wet_timer = self.ball.wet_debuff_timer

    if wet_timer > 0.0:
        wet_timer -= delta
        if wet_timer <= 0.0:
            if typeof(self.ball) == TYPE_DICTIONARY:
                if self.ball.has("base_speed"):
                    self.ball["base_speed"] /= 0.8
                self.ball["wet_debuff_timer"] = 0.0
            else:
                if "base_speed" in self.ball:
                    self.ball.base_speed /= 0.8
                self.ball.wet_debuff_timer = 0.0
        else:
            if typeof(self.ball) == TYPE_DICTIONARY:
                self.ball["wet_debuff_timer"] = wet_timer
            else:
                self.ball.wet_debuff_timer = wet_timer

    # Decrement submerge_timer
    var submerge_timer = 0.0
    if typeof(self.ball) == TYPE_DICTIONARY:
        if self.ball.has("submerge_timer"):
            submerge_timer = self.ball["submerge_timer"]
    else:
        if "submerge_timer" in self.ball:
            submerge_timer = self.ball.submerge_timer

    if submerge_timer > 0.0:
        submerge_timer -= delta
        if submerge_timer <= 0.0:
            if typeof(self.ball) == TYPE_DICTIONARY:
                self.ball["is_submerged"] = false
                self.ball["submerge_timer"] = 0.0
            else:
                self.ball.is_submerged = false
                self.ball.submerge_timer = 0.0
        else:
            if typeof(self.ball) == TYPE_DICTIONARY:
                self.ball["submerge_timer"] = submerge_timer
            else:
                self.ball.submerge_timer = submerge_timer
""")

with open("src/ai/action.gd", "w") as f:
    f.writelines(lines)
