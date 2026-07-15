import re

with open("src/ai/test_extreme_weather.py", "r") as f:
    content = f.read()

search_str2 = """    # Now simulate action.py logic to neutralize the acid on b1 using a neutralizing puddle
    from ai.action import Action
    world.arena.hazards.append(MockHazard("neutralizing_puddle", 100.0, 100.0, 40.0))
    action1 = Action(b1, world)"""

replace_str2 = """    # Now simulate action.py logic to neutralize the acid on b1 using a neutralizing puddle
    from ai.action import Action
    if not hasattr(world.arena, "hazards"):
        world.arena.hazards = []
    world.arena.hazards.append(MockHazard("neutralizing_puddle", 100.0, 100.0, 40.0))

    b1.vx = 0.0
    b1.vy = 0.0
    b1.team = "team1"
    b1.is_turret = False

    world.next_id = 9999

    action1 = Action(b1, world)"""

content = content.replace(search_str2, replace_str2)

with open("src/ai/test_extreme_weather.py", "w") as f:
    f.write(content)
