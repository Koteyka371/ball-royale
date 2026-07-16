import json

with open("agent_tasks.json", "r") as f:
    data = json.load(f)

for task in data["tasks"]:
    if task["id"] == "idea-890":
        task["status"] = "done"

with open("agent_tasks.json", "w") as f:
    json.dump(data, f, indent=2)
