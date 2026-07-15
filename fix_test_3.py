import re

with open("src/ai/test_extreme_weather.py", "r") as f:
    content = f.read()

search_str3 = """    # Give ball dummy attributes to pass action initialization if needed, although mostly it relies on MockWorld
    # We tick action to process the hazard
    # In order not to crash on other logic, we can just test the puddle logic directly or rely on action.execute()
    # It might be easier to run a simplified tick of action
    world.events = []
    action1.execute()"""

replace_str3 = """    world.events = []

    b1.action = "idle"

    if not hasattr(world.arena, "items"): world.arena.items = []
    world.balls = [b1]

    # Just mock the _resolve_collisions to prevent crashes
    orig_resolve = action1._resolve_collisions
    action1._resolve_collisions = lambda *args, **kwargs: None

    action1.execute("idle", 1.0)"""

content = content.replace(search_str3, replace_str3)

with open("src/ai/test_extreme_weather.py", "w") as f:
    f.write(content)
