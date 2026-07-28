import subprocess
import os

with open("test_script.gd", "w") as f:
    f.write("""extends SceneTree
def _init():
    print("This would test the GDScript code")
    quit()
""")

print("Testing python script:")
os.system("python scripts/test_physical_modes.py --fast")
