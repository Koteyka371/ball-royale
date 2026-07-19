import re
import sys

def modify_game_modes_py():
    path = "src/ai/game_modes.py"
    with open(path, "r") as f:
        content = f.read()

    orig_slippery = """                # slide more
                if hasattr(b, "vx") and hasattr(b, "vy"):
                    b.x += getattr(b, "vx") * delta * 0.5
                    b.y += getattr(b, "vy") * delta * 0.5"""
    repl_slippery = """                # slide more
                if hasattr(b, "vx") and hasattr(b, "vy") and getattr(b, "slippery_immunity_timer", 0.0) <= 0.0:
                    b.x += getattr(b, "vx") * delta * 0.5
                    b.y += getattr(b, "vy") * delta * 0.5"""

    orig_rain_dash = """                # rain makes surface slippery/increases dash range but reduces steering
                b.dash_range_mult = 1.5
                b.steering_mult = 0.5"""
    repl_rain_dash = """                # rain makes surface slippery/increases dash range but reduces steering
                if getattr(b, "slippery_immunity_timer", 0.0) <= 0.0:
                    b.dash_range_mult = 1.5
                    b.steering_mult = 0.5"""

    content = content.replace(orig_slippery, repl_slippery)
    content = content.replace(orig_rain_dash, repl_rain_dash)

    orig_ice = """                setattr(b, "friction_multiplier", 0.1) # extremely slippery
                if hasattr(b, "hp"): b.hp -= 1.0 * delta # freezing damage"""
    repl_ice = """                if getattr(b, "freezing_immunity_timer", 0.0) <= 0.0:
                    setattr(b, "friction_multiplier", 0.1) # extremely slippery
                    if hasattr(b, "hp"): b.hp -= 1.0 * delta # freezing damage"""
    content = content.replace(orig_ice, repl_ice)

    # Check for where GameMode ticks to reduce timers
    orig_tick_timer = """            w_timer = getattr(b, 'weather_immunity_timer', 0.0)
            is_immune = (w_timer > 0.0) if isinstance(w_timer, (int, float)) else False"""
    repl_tick_timer = """            w_timer = getattr(b, 'weather_immunity_timer', 0.0)
            is_immune = (w_timer > 0.0) if isinstance(w_timer, (int, float)) else False

            fi_timer = getattr(b, 'freezing_immunity_timer', 0.0)
            if fi_timer > 0.0:
                b.freezing_immunity_timer = max(0.0, fi_timer - delta)
            si_timer = getattr(b, 'slippery_immunity_timer', 0.0)
            if si_timer > 0.0:
                b.slippery_immunity_timer = max(0.0, si_timer - delta)"""

    content = content.replace(orig_tick_timer, repl_tick_timer)

    with open(path, "w") as f:
        f.write(content)

modify_game_modes_py()
