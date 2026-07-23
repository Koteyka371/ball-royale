import re

file_path = "src/ai/action.py"
with open(file_path, "r") as f:
    content = f.read()

hazard_logic = """                    elif hazard.kind == "sticky_mud_puddle":
                        current_tick = getattr(self.world, "tick", 0)
                        last_updated = getattr(hazard, "last_updated_tick", -1)
                        if last_updated != current_tick:
                            hazard.last_updated_tick = current_tick
                            hazard.duration = getattr(hazard, "duration", 10.0) - delta
                            if hazard.duration <= 0:
                                hazard.active = False
                                continue

                            # Apply debuff to balls in radius
                            for b in self.world.balls:
                                if getattr(b, "alive", True):
                                    hx = getattr(hazard, "x", 0)
                                    hy = getattr(hazard, "y", 0)
                                    bx = getattr(b, "x", 0)
                                    by = getattr(b, "y", 0)
                                    dist_sq = (hx - bx)**2 + (hy - by)**2
                                    rad_sum = hazard.radius + getattr(b, "radius", 20.0)
                                    if dist_sq < rad_sum * rad_sum:
                                        b.mud_debuff_timer = 3.0
                                        current_stacks = getattr(b, "mud_debuff_stacks", 0)
                                        stack_cooldown = getattr(b, "mud_stack_cooldown", 0.0)
                                        if stack_cooldown <= 0:
                                            b.mud_debuff_stacks = min(current_stacks + 1, 5)
                                            b.mud_stack_cooldown = 0.5
                                        else:
                                            b.mud_stack_cooldown -= delta"""

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

                            # Check for enemy proximity
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
                                hazard.active = False
                                # Apply mud to everyone in 60 radius
                                for b in self.world.balls:
                                    if getattr(b, "alive", True):
                                        bx = getattr(b, "x", 0)
                                        by = getattr(b, "y", 0)
                                        dist_sq = (hx - bx)**2 + (hy - by)**2
                                        rad_sum = getattr(hazard, "radius", 60.0) + getattr(b, "radius", 20.0)
                                        if dist_sq <= rad_sum * rad_sum:
                                            b.mud_debuff_timer = 5.0
                                            b.mud_debuff_stacks = 5 # Instant max stacks
                                            b.mud_stack_cooldown = 1.0

""" + hazard_logic

content = content.replace(hazard_logic, new_hazard_logic)

with open(file_path, "w") as f:
    f.write(content)
