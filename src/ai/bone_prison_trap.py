from typing import Any, List
import math

class BonePrisonTrapMode:
    def __init__(self):
        self.name = "Bone Prison Trap"
        self.description = "Skill that drops a trap which entombs an enemy in a bone prison, disabling movement and providing a destructible shell."

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:
        if not hasattr(world, "arena") or not hasattr(world.arena, "hazards"):
            return

        hazards_to_remove = []
        new_hazards = []

        for h in world.arena.hazards:
            if getattr(h, "kind", "") == "bone_prison":
                # Check for duration expiry
                if hasattr(h, "duration"):
                    h.duration -= delta
                    if h.duration <= 0:
                        hazards_to_remove.append(h)

                        # Free the trapped ball
                        trapped_id = getattr(h, "trapped_ball_id", None)
                        if trapped_id is not None:
                            for b in balls:
                                if getattr(b, "id", None) == trapped_id:
                                    setattr(b, "trapped", False)
                                    setattr(b, "bone_prison_id", None)
                                    break
                        continue

                # Trap logic: check if broken (0 HP)
                if getattr(h, "hp", 1.0) <= 0:
                    hazards_to_remove.append(h)
                    trapped_id = getattr(h, "trapped_ball_id", None)
                    if trapped_id is not None:
                        for b in balls:
                            if getattr(b, "id", None) == trapped_id:
                                setattr(b, "trapped", False)
                                setattr(b, "bone_prison_id", None)
                                break
                    continue

                # Constrain trapped ball
                trapped_id = getattr(h, "trapped_ball_id", None)
                if trapped_id is not None:
                    for b in balls:
                        if getattr(b, "id", None) == trapped_id:
                            # Keep it in place
                            setattr(b, "x", getattr(h, "x", 0.0))
                            setattr(b, "y", getattr(h, "y", 0.0))
                            setattr(b, "vx", 0.0)
                            setattr(b, "vy", 0.0)
                            setattr(b, "speed", 0.0)
                            setattr(b, "trapped", True)
                            setattr(b, "bone_prison_id", getattr(h, "id", None))
                            break

            elif getattr(h, "kind", "") == "bone_prison_trap":
                # Activation delay
                if hasattr(h, "activation_timer"):
                    h.activation_timer -= delta
                    if h.activation_timer > 0:
                        continue

                # Check for enemies nearby
                for b in balls:
                    if getattr(b, "alive", False) and getattr(b, "team", "") != getattr(h, "owner_team", ""):
                        dist = math.hypot(getattr(b, "x", 0.0) - getattr(h, "x", 0.0), getattr(b, "y", 0.0) - getattr(h, "y", 0.0))

                        if dist <= getattr(h, "radius", 30.0) + getattr(b, "radius", 15.0):
                            hazards_to_remove.append(h)

                            # Create the actual prison
                            prison_id = getattr(world, "next_id", 99999)
                            if hasattr(world, "next_id"):
                                world.next_id += 1

                            class SimplePrison:
                                def __init__(self, pid, px, py):
                                    self.id = pid; self.x = px; self.y = py; self.radius = 20.0; self.kind = "bone_prison"; self.damage = 0.0
                            prison = SimplePrison(prison_id, getattr(b, "x", 0.0), getattr(b, "y", 0.0))

                            setattr(prison, "duration", getattr(h, "prison_duration", 3.0))
                            setattr(prison, "hp", getattr(h, "prison_hp", 50.0))
                            setattr(prison, "trapped_ball_id", getattr(b, "id", None))
                            setattr(prison, "owner_team", getattr(h, "owner_team", ""))

                            new_hazards.append(prison)

                            setattr(b, "trapped", True)
                            setattr(b, "bone_prison_id", prison_id)
                            break

        for h in hazards_to_remove:
            if h in world.arena.hazards:
                world.arena.hazards.remove(h)

        world.arena.hazards.extend(new_hazards)
