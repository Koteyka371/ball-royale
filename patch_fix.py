import re
import sys

def modify_game_modes_py():
    path = "src/ai/game_modes.py"
    with open(path, "r") as f:
        content = f.read()

    orig_tick_timer = """            fi_timer = getattr(b, 'freezing_immunity_timer', 0.0)
            if fi_timer > 0.0:
                b.freezing_immunity_timer = max(0.0, fi_timer - delta)
            si_timer = getattr(b, 'slippery_immunity_timer', 0.0)
            if si_timer > 0.0:
                b.slippery_immunity_timer = max(0.0, si_timer - delta)"""
    repl_tick_timer = """            fi_timer = getattr(b, 'freezing_immunity_timer', 0.0)
            if isinstance(fi_timer, (int, float)) and fi_timer > 0.0:
                b.freezing_immunity_timer = max(0.0, fi_timer - delta)
            si_timer = getattr(b, 'slippery_immunity_timer', 0.0)
            if isinstance(si_timer, (int, float)) and si_timer > 0.0:
                b.slippery_immunity_timer = max(0.0, si_timer - delta)"""

    content = content.replace(orig_tick_timer, repl_tick_timer)

    with open(path, "w") as f:
        f.write(content)

modify_game_modes_py()
