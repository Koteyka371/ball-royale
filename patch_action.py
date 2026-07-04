import re

with open("src/ai/action.py", "r") as f:
    content = f.read()

timer_code = """        if getattr(self.ball, "emp_immunity_timer", 0.0) > 0:
            self.ball.emp_immunity_timer -= delta
            if self.ball.emp_immunity_timer < 0:
                self.ball.emp_immunity_timer = 0.0"""

new_timer_code = """        if getattr(self.ball, "emp_immunity_timer", 0.0) > 0:
            self.ball.emp_immunity_timer -= delta
            if self.ball.emp_immunity_timer < 0:
                self.ball.emp_immunity_timer = 0.0
        if getattr(self.ball, "immunity_timer", 0.0) > 0:
            self.ball.immunity_timer -= delta
            if self.ball.immunity_timer < 0:
                self.ball.immunity_timer = 0.0"""

if timer_code in content:
    content = content.replace(timer_code, new_timer_code)
    with open("src/ai/action.py", "w") as f:
        f.write(content)
    print("Patched action.py")
else:
    print("Could not find timer code in action.py")
