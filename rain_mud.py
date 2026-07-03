with open('src/ai/action.gd', 'r') as f:
    text = f.read()

import re
matches = list(re.finditer(r"# Occasional slow debuff that lingers", text))
for m in matches:
    print(text[m.start():m.start()+1500])
