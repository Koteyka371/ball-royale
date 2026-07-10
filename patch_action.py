import re

with open("src/ai/action.py", "r") as f:
    content = f.read()

# Add `massive_gravity_well` hazard logic to `action.py`.
# It acts similarly to gravity_well, so we should add "massive_gravity_well" where "gravity_well" is.
# BUT wait! The task says:
# "An extremely large, slow-moving hazard that acts similarly to the gravity well but actively sucks in surrounding small hazards (like traps or spikes) and grows larger. It tests players' abilities to use boosts or specific game modes to escape its ever-increasing event horizon."
