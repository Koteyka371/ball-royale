import urllib.request, json
r = urllib.request.urlopen('https://api.github.com/repos/Koteyka371/ball-royale/pulls?state=open&per_page=20')
data = json.load(r)
print(f'Open PRs: {len(data)}')
for p in data:
    print(f'  #{p["number"]} {p["title"][:60]}')

r2 = urllib.request.urlopen('https://api.github.com/repos/Koteyka371/ball-royale/actions/runs?per_page=5')
runs = json.load(r2)
print(f'\nRecent workflow runs:')
for run in runs.get('workflow_runs', []):
    print(f'  {run["name"][:30]:30s} {run["status"]:12s} {run.get("conclusion","")}')
