import re

file_path = "src/ai/action.py"
with open(file_path, "r") as f:
    content = f.read()

hazard_logic_re = r'                    elif hazard\.kind == "proximity_mud_puddle":.*?(?=                    elif hazard\.kind == "sticky_mud_puddle":)'
new_hazard_logic = """                    elif hazard.kind == "proximity_mud_puddle":
                        current_tick = getattr(self.world, "tick", 0)
                        last_updated = getattr(hazard, "last_updated_tick", -1)
                        if last_updated != current_tick:
                            hazard.last_updated_tick = current_tick
                            hazard.duration = getattr(hazard, "duration", 30.0) - delta
                            if hazard.duration <= 0:
                                hazard.active = False
                                continue

                            hx = getattr(hazard, "x", 0)
                            hy = getattr(hazard, "y", 0)

                            is_triggered = getattr(hazard, "is_triggered", False)

                            if not is_triggered:
                                # Check for enemy proximity to trigger
                                triggered = False
                                owner_id = getattr(hazard, "owner_id", None)
                                trigger_radius = 40.0
                                for b in self.world.balls:
                                    if getattr(b, "alive", True) and getattr(b, "id", None) != owner_id:
                                        bx = getattr(b, "x", 0)
                                        by = getattr(b, "y", 0)
                                        dist_sq = (hx - bx)**2 + (hy - by)**2
                                        if dist_sq <= trigger_radius * trigger_radius:
                                            triggered = True
                                            break

                                if triggered:
                                    hazard.is_triggered = True
                                    hazard.duration = 10.0 # Stays as puddle for 10s

                            if getattr(hazard, "is_triggered", False):
                                # Apply mud to everyone in 60 radius (persistent puddle)
                                for b in self.world.balls:
                                    if getattr(b, "alive", True):
                                        bx = getattr(b, "x", 0)
                                        by = getattr(b, "y", 0)
                                        dist_sq = (hx - bx)**2 + (hy - by)**2
                                        rad_sum = getattr(hazard, "radius", 60.0) + getattr(b, "radius", 20.0)
                                        if dist_sq <= rad_sum * rad_sum:
                                            b.mud_debuff_timer = 5.0
                                            b.mud_debuff_stacks = 5 # Instant max stacks for heavy slow
                                            b.mud_stack_cooldown = 1.0
                                            # Apply continuous small damage
                                            if hasattr(b, "hp"):
                                                b.hp -= 20.0 * delta
                                                if b.hp <= 0:
                                                    b.alive = False
                                                    b.hp = 0
                                                    b.killer = "proximity_mud_puddle"

"""

content = re.sub(hazard_logic_re, new_hazard_logic, content, flags=re.DOTALL)

with open(file_path, "w") as f:
    f.write(content)
