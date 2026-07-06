import pytest
from ai.perception import Perception

# Let's inspect test_sonar_ping_perception_smoke failure.
# enemy x=60, ball x=0. smoke x=30, radius 80. ball x=0 is inside smoke!
# "If in smoke: perception_radius = min(perception_radius, 50.0)"
# Since perception_radius = 50.0, enemy at 60 is outside radius!

print("Done")
