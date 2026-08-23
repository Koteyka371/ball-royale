import re

with open('src/ai/action.gd', 'r') as f:
    content = f.read()

# Replace tabs with spaces for the specific block if necessary,
# or just re-write the regex to ensure correct spacing.
# The original lines used spaces:
#             elif typeof(nearest) == TYPE_DICTIONARY and nearest.has("kind") and nearest["kind"] == "sticky_bomb_booster":

fixed = content.replace(
'''            elif typeof(nearest) == TYPE_DICTIONARY and nearest.has("kind") and nearest["kind"] == "fire_sticky_bomb_booster":
					ball.active_skill = "fire_sticky_bomb"
					ball.skill_timer = 4.0
					if typeof(world) == TYPE_DICTIONARY and world.has("arena") and typeof(world["arena"]) == TYPE_DICTIONARY and world["arena"].has("hazards"):
						world["arena"]["hazards"].erase(nearest)
					elif typeof(world) == TYPE_OBJECT and world.get("arena") != null and typeof(world.arena) == TYPE_OBJECT and world.arena.get("hazards") != null:
						world.arena.hazards.erase(nearest)
					if typeof(world) == TYPE_DICTIONARY and world.has("boosters"):
						world["boosters"].erase(nearest)
					elif typeof(world) == TYPE_OBJECT and world.get("boosters") != null:
						world.boosters.erase(nearest)
				elif typeof(nearest) == TYPE_DICTIONARY and nearest.has("kind") and nearest["kind"] == "sticky_bomb_booster":''',
'''            elif typeof(nearest) == TYPE_DICTIONARY and nearest.has("kind") and nearest["kind"] == "fire_sticky_bomb_booster":
                ball.active_skill = "fire_sticky_bomb"
                ball.skill_timer = 4.0
                if typeof(world) == TYPE_DICTIONARY and world.has("arena") and typeof(world["arena"]) == TYPE_DICTIONARY and world["arena"].has("hazards"):
                    world["arena"]["hazards"].erase(nearest)
                elif typeof(world) == TYPE_OBJECT and world.get("arena") != null and typeof(world.arena) == TYPE_OBJECT and world.arena.get("hazards") != null:
                    world.arena.hazards.erase(nearest)
                if typeof(world) == TYPE_DICTIONARY and world.has("boosters"):
                    world["boosters"].erase(nearest)
                elif typeof(world) == TYPE_OBJECT and world.get("boosters") != null:
                    world.boosters.erase(nearest)
            elif typeof(nearest) == TYPE_DICTIONARY and nearest.has("kind") and nearest["kind"] == "sticky_bomb_booster":'''
)

with open('src/ai/action.gd', 'w') as f:
    f.write(fixed)
