import sys

def patch_action_gd():
    with open('src/ai/action.gd', 'r') as f:
        content = f.read()

    search_str = """					var trap_type = "mine"
					var r = randf()
					if r > 0.75:
						trap_type = "freeze"
					elif r > 0.5:
						trap_type = "black_hole"
					elif r > 0.25:
						trap_type = "swap"
					trap.set_meta("trap_variant", trap_type)"""

    replace_str = """					var trap_type = "mine"
					var r = randf()
					if r > 0.8:
						trap_type = "freeze"
					elif r > 0.6:
						trap_type = "black_hole"
					elif r > 0.4:
						trap_type = "swap"
					elif r > 0.2:
						trap_type = "reverse_gravity"
					trap.set_meta("trap_variant", trap_type)"""

    if search_str in content:
        content = content.replace(search_str, replace_str, 1)
        with open('src/ai/action.gd', 'w') as f:
            f.write(content)
        print("Patched GDScript random choice.")
    else:
        print("Could not find the GDScript random choice string.")

if __name__ == "__main__":
    patch_action_gd()
