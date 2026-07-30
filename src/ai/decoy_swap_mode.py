import math
import copy
import random
from ai.game_modes import GameMode

class DecoySwapSurvivalMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Decoy Swap Survival"
        self.description = "A chaotic new game mode where periodically every player on the map is instantly swapped in position with their nearest active decoy or clone. If they do not have a decoy active, one is spawned for them at their location moments before the swap."
        self.swap_timer = 0.0
        self.swap_interval = 10.0

    def tick(self, world, balls, delta=0.016):
        self.swap_timer += delta

        if self.swap_timer >= self.swap_interval:
            self.swap_timer = 0.0

            if hasattr(world, "add_event"):
                world.add_event("decoy_swap_event", {"message": "Position Swap Initiated!"})

            new_decoys = []

            # Find eligible players
            players = []
            for b in balls:
                if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator" and not getattr(b, "is_decoy", False):
                    players.append(b)

            for p in players:
                # Find nearest active decoy owned by p, or any decoy if owner_id not set but let's just find nearest decoy with same team if we can't find owned
                # Better: since we want THEIR decoy or clone, check owner_id == p.id
                nearest_decoy = None
                nearest_dist = float('inf')

                for d in balls:
                    if getattr(d, "alive", False) and getattr(d, "is_decoy", False):
                        is_owned = False
                        if getattr(d, "owner_id", None) == getattr(p, "id", None):
                            is_owned = True
                        elif getattr(d, "team", None) == getattr(p, "team", None):
                            # Fallback if owner_id not strictly used, though usually it is.
                            # Let's consider any decoy of the same team as "theirs" if owner_id is missing, but prefer owner_id.
                            is_owned = True

                        if is_owned:
                            dist = math.hypot(d.x - p.x, d.y - p.y)
                            if dist < nearest_dist:
                                nearest_dist = dist
                                nearest_decoy = d

                if nearest_decoy is None:
                    # Spawn one at their location moments before the swap
                    decoy = copy.copy(p)
                    if hasattr(world, "next_id"):
                        decoy.id = world.next_id
                        world.next_id += 1
                    else:
                        decoy.id = random.randint(100000, 999999)

                    decoy.is_decoy = True
                    decoy.ball_type = "mimic_decoy"
                    decoy.owner_id = getattr(p, "id", None)
                    decoy.speed = 0.0
                    decoy.damage = 0.0
                    decoy.base_speed = 0.0
                    decoy.x = p.x
                    decoy.y = p.y

                    new_decoys.append(decoy)
                    nearest_decoy = decoy

                # Swap!
                temp_x = p.x
                temp_y = p.y

                p.x = nearest_decoy.x
                p.y = nearest_decoy.y

                nearest_decoy.x = temp_x
                nearest_decoy.y = temp_y

                if hasattr(world, "add_event"):
                    world.add_event("visual_effect", {"type": "teleport", "x": p.x, "y": p.y})
                    world.add_event("visual_effect", {"type": "teleport", "x": nearest_decoy.x, "y": nearest_decoy.y})

            if hasattr(world, "balls"):
                for d in new_decoys:
                    world.balls.append(d)
