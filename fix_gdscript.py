import re

with open('src/ai/action.gd', 'r') as f:
    text = f.read()

# Fix 1: The issue with dist_sq scope
# We should change the condition from:
# if not hit_entities.has(e):
#   var has_ins = false
#   ...
#   if not has_ins:
#       var dist_sq = ...
#
# To:
# if not hit_entities.has(e):
#   var has_ins = false
#   ...
#   if not has_ins:
#       var dist_sq = pow(...)
#       if dist_sq < chain_range_sq:
#           nearby.append(...)
#
# Wait, the code already has `if dist_sq < chain_range_sq:` inside the same block as before, but I need to check the original.
