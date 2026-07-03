import json

try:
    with open('agent_tasks.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        tasks = data.get('tasks', data) if isinstance(data, dict) else data
        for task in tasks:
            if task.get('status') == 'todo':
                print(task)
except Exception as e:
    pass
