with open("src/ai/action.py", "r") as f:
    content = f.read()

# Replace local random imports inside execute which shadow the global import in certain execution paths
import re
# We should just ensure `import random` isn't repeatedly imported inside inner functions that cause unbound local errors
content = re.sub(r'^[ \t]*import random\n', '', content, flags=re.MULTILINE)
# Add it back to top if we removed it
if not content.startswith('import random'):
    content = 'import random\n' + content

with open("src/ai/action.py", "w") as f:
    f.write(content)
