import json

with open("agent_tasks.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for task in data.get("tasks", []):
    if task["title"] == "Implement Perception system":
        task["status"] = "done"

with open("agent_tasks.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Marked 'Implement Perception system' as done.")
