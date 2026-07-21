import subprocess
try:
    subprocess.run(["godot", "--headless", "--check-only", "-s", "src/ai/action.gd"], check=True, capture_output=True)
    print("Syntax OK")
except Exception as e:
    print("Cannot run godot or syntax failed")
