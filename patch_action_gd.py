with open("src/ai/action.gd", "r") as f:
    gd_content = f.read()

gd_timer_code = """        var emp_imm_timer = 0.0
        if "emp_immunity_timer" in self.ball:
            emp_imm_timer = float(self.ball.emp_immunity_timer)
        elif self.ball.has_method("get_meta") and self.ball.has_meta("emp_immunity_timer"):
            emp_imm_timer = float(self.ball.get_meta("emp_immunity_timer"))
        if emp_imm_timer > 0:
            emp_imm_timer -= delta
            if emp_imm_timer < 0:
                emp_imm_timer = 0.0
            if "emp_immunity_timer" in self.ball:
                self.ball.emp_immunity_timer = emp_imm_timer
            if self.ball.has_method("set_meta"):
                self.ball.set_meta("emp_immunity_timer", emp_imm_timer)"""

gd_new_timer_code = """        var emp_imm_timer = 0.0
        if "emp_immunity_timer" in self.ball:
            emp_imm_timer = float(self.ball.emp_immunity_timer)
        elif self.ball.has_method("get_meta") and self.ball.has_meta("emp_immunity_timer"):
            emp_imm_timer = float(self.ball.get_meta("emp_immunity_timer"))
        if emp_imm_timer > 0:
            emp_imm_timer -= delta
            if emp_imm_timer < 0:
                emp_imm_timer = 0.0
            if "emp_immunity_timer" in self.ball:
                self.ball.emp_immunity_timer = emp_imm_timer
            if self.ball.has_method("set_meta"):
                self.ball.set_meta("emp_immunity_timer", emp_imm_timer)

        var imm_timer = 0.0
        if "immunity_timer" in self.ball:
            imm_timer = float(self.ball.immunity_timer)
        elif self.ball.has_method("get_meta") and self.ball.has_meta("immunity_timer"):
            imm_timer = float(self.ball.get_meta("immunity_timer"))
        if imm_timer > 0:
            imm_timer -= delta
            if imm_timer < 0:
                imm_timer = 0.0
            if "immunity_timer" in self.ball:
                self.ball.immunity_timer = imm_timer
            if self.ball.has_method("set_meta"):
                self.ball.set_meta("immunity_timer", imm_timer)"""

if gd_timer_code in gd_content:
    gd_content = gd_content.replace(gd_timer_code, gd_new_timer_code)
    with open("src/ai/action.gd", "w") as f:
        f.write(gd_content)
    print("Patched action.gd")
else:
    print("Could not find timer code in action.gd")
