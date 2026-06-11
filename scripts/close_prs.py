import urllib.request
import json
import sys

repo = "Koteyka371/ball-royale"

# Close PRs #2-#13
for i in range(2, 14):
    url = f"https://api.github.com/repos/{repo}/pulls/{i}"
    data = json.dumps({"state": "closed"}).encode()
    req = urllib.request.Request(url, data=data, method="PATCH")
    req.add_header("Accept", "application/vnd.github.v3+json")
    try:
        resp = urllib.request.urlopen(req)
        result = json.load(resp)
        print(f"PR #{i}: {result.get('state', 'unknown')}")
    except Exception as e:
        print(f"PR #{i}: error - {e}")

# Show remaining open PRs
url = f"https://api.github.com/repos/{repo}/pulls?state=open&per_page=20"
req = urllib.request.Request(url)
resp = urllib.request.urlopen(req)
prs = json.load(resp)
print(f"\nOpen PRs: {len(prs)}")
for p in prs:
    print(f"  #{p['number']} {p['title'][:60]}")
