import random
from typing import List, Any

class InteractiveCrowdHazards:
    @staticmethod
    def process_boredom(excitement_level: float, balls: List[Any], world: Any) -> float:
        if excitement_level >= 20.0:
            return excitement_level

        boredom = 20.0 - excitement_level

        # Chance scales from 1% at 19 excitement to ~20% at 0 excitement
        spawn_chance = 0.01 + (boredom / 20.0) * 0.19

        if random.random() < spawn_chance:
            alive_balls = [b for b in balls if getattr(b, "alive", False) and getattr(b, "ball_type", "") != "spectator"]
            if not alive_balls:
                return excitement_level

            # Number of hazards scales from 1 to 3
            num_hazards = 1 + int((boredom / 20.0) * 2)

            # Hazard pool expands at high boredom
            hazard_pool = ["temporary_wall", "slow_field"]
            if boredom > 10.0:
                hazard_pool.append("mini_bomb")

            for _ in range(num_hazards):
                target_ball = random.choice(alive_balls)
                hazard_kind = random.choice(hazard_pool)

                if hasattr(world, 'add_event'):
                    world.add_event("spawn_hazard", {
                        "x": getattr(target_ball, "x", 0) + random.uniform(-50, 50),
                        "y": getattr(target_ball, "y", 0) + random.uniform(-50, 50),
                        "kind": hazard_kind
                    })

            if hasattr(world, 'add_event'):
                message = "The crowd boos and throws hazards into the arena!" if num_hazards > 1 else "The crowd boos and throws a hazard into the arena!"
                world.add_event("crowd_throw", {"message": message})

            excitement_level += 5.0 + (num_hazards * 2.0)

        return excitement_level
