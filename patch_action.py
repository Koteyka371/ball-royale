with open("src/ai/action.py", "r") as f:
    content = f.read()

speed_patch = """
            if hasattr(self.ball, "physics_anomaly_speed_mod"):
                self.ball.vx *= self.ball.physics_anomaly_speed_mod
                self.ball.vy *= self.ball.physics_anomaly_speed_mod

            if hasattr(self.ball, "_reflection_vx"):
"""

content = content.replace("            if hasattr(self.ball, \"_reflection_vx\"):", speed_patch)

with open("src/ai/action.py", "w") as f:
    f.write(content)
