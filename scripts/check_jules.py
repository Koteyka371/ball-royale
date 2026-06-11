import urllib.request, json

# Get latest run
r = urllib.request.urlopen('https://api.github.com/repos/Koteyka371/ball-royale/actions/runs?per_page=1')
run = json.load(r)['workflow_runs'][0]
print(f"Run ID: {run['id']}")
print(f"Status: {run['status']}")
print(f"Conclusion: {run.get('conclusion','')}")
print(f"URL: {run['html_url']}")
print(f"Created: {run['created_at']}")

# Check latest commits from Jules
r2 = urllib.request.urlopen('https://api.github.com/repos/Koteyka371/ball-royale/commits?per_page=20')
commits = json.load(r2)
jules_commits = [c for c in commits if 'jules' in c['commit']['author']['name'].lower() or 'jules' in c['commit']['message'].lower()]
print(f"\nJules commits: {len(jules_commits)}")
for c in jules_commits[:5]:
    msg = c['commit']['message'].split('\n')[0][:80]
    print(f"  {c['commit']['author']['name']}: {msg}")

# Check task status
with open('agent_tasks.json') as f:
    data = json.load(f)
done = [t['id'] for t in data['tasks'] if t['status'] == 'done']
todo = [t['id'] for t in data['tasks'] if t['status'] == 'todo']
print(f"\nTasks: {len(done)} done, {len(todo)} todo")
