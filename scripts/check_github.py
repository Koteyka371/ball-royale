import urllib.request, json

# Check workflow runs
r = urllib.request.urlopen('https://api.github.com/repos/Koteyka371/ball-royale/actions/runs?per_page=5')
runs = json.load(r)
print("=== Recent workflow runs ===")
for run in runs.get('workflow_runs', []):
    print(f"  {run['name']:30s} {run['status']:12s} {run.get('conclusion',''):10s} {run['created_at'][:16]}")

# Check open PRs
r2 = urllib.request.urlopen('https://api.github.com/repos/Koteyka371/ball-royale/pulls?state=open&per_page=10')
prs = json.load(r2)
print(f"\n=== Open PRs: {len(prs)} ===")
for p in prs:
    print(f"  #{p['number']} {p['title'][:60]}")

# Check recent commits
r3 = urllib.request.urlopen('https://api.github.com/repos/Koteyka371/ball-royale/commits?per_page=8')
commits = json.load(r3)
print(f"\n=== Recent commits ===")
for c in commits:
    msg = c['commit']['message'].split('\n')[0][:60]
    author = c['commit']['author']['name']
    print(f"  {author:20s} {msg}")
