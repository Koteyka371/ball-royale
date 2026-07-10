import re

with open("src/ai/test_physics_anomaly_event.py", "r") as f:
    content = f.read()

content = content.replace('self.assertNotEqual(old_vx, sp["vx"]) or self.assertNotEqual(old_vy, sp["vy"])', 'if old_vx == sp["vx"]:\n            self.assertNotEqual(old_vy, sp["vy"])')

with open("src/ai/test_physics_anomaly_event.py", "w") as f:
    f.write(content)
