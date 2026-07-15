import re

with open('src/ai/action.py', 'r') as f:
    content = f.read()

# modify temporal rift pull? It doesn't seem to pull, it scales delta.
# The prompt: "heavily reduces knockback and pull effects from emp traps, temporal rifts, and black holes"
# wait, temporal rift might have a pull somewhere else?
