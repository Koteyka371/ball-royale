import os
for root, dirs, files in os.walk("src"):
    for file in files:
        if file.endswith((".py", ".gd")):
            with open(os.path.join(root, file), 'r') as f:
                for line in f:
                    if "match_over" in line or "winner" in line or "end_match" in line:
                        print(f"{os.path.join(root, file)}: {line.strip()}")
