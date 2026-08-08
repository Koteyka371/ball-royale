from typing import Any, List
from ai.game_modes import GameMode

class GhostCompanionMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Ghost Companion"
        self.description = "Eliminated players spawn as ghosts that can attach to living players, applying small buffs or debuffs."
        self.ghosts = {}

    def setup(self, world: 'Any', balls: 'List[Any]') -> None:
        super().setup(world, balls)
        self.ghosts = {}
        if not hasattr(world, "dead_balls"):
            world.dead_balls = []

    def tick(self, world: 'Any', balls: 'List[Any]', delta: float = 0.016) -> None:
        super().tick(world, balls, delta)
        import math

        for b in balls:
            b_id = getattr(b, "id", None)
            if b_id is None or getattr(b, "ball_type", None) == "spectator":
                continue

            hp = getattr(b, "hp", 100.0)
            is_ghost = getattr(b, "is_ghost", False)

            if hp <= 0 and not is_ghost:
                b.is_ghost = True
                b.ghost_target_id = None
                b.alive = True
                b.max_hp = 50.0
                b.hp = 50.0
                b.speed = 150.0
                b.damage = 0.0
                if b_id in world.dead_balls:
                    world.dead_balls.remove(b_id)
                self.ghosts[b_id] = b

        # Handle ghosts attaching to players
        for b in balls:
            if getattr(b, "is_ghost", False):
                b_id = getattr(b, "id", None)
                target_id = getattr(b, "ghost_target_id", None)

                # Unattach if target died or is triggered hazard
                if target_id is not None:
                    target_b = next((x for x in balls if getattr(x, "id", None) == target_id), None)
                    if not target_b and hasattr(world, "arena") and hasattr(world.arena, "hazards"):
                        target_b = next((x for x in world.arena.hazards if getattr(x, "id", None) == target_id), None)
                        if target_b and (getattr(target_b, "triggered", False) or getattr(target_b, "active", False)):
                            target_b = None

                    if not target_b or (target_b in balls and (not getattr(target_b, "alive", False) or getattr(target_b, "is_ghost", False))):
                        b.ghost_target_id = None
                        target_id = None

                # Find new target or move towards existing target
                if target_id is None:
                    min_dist = 999999
                    best_target = None
                    for ob in balls:
                        if getattr(ob, "alive", True) and not getattr(ob, "is_ghost", False) and getattr(ob, "ball_type", None) != "spectator":
                            d = (ob.x - b.x)**2 + (ob.y - b.y)**2
                            if d < min_dist:
                                min_dist = d
                                best_target = ob

                    if not best_target and hasattr(world, "arena") and hasattr(world.arena, "hazards"):
                        for h in world.arena.hazards:
                            if not getattr(h, "triggered", False) and not getattr(h, "active", False):
                                d = (getattr(h, "x", 0) - b.x)**2 + (getattr(h, "y", 0) - b.y)**2
                                if d < min_dist:
                                    min_dist = d
                                    best_target = h

                    if best_target:
                        # Fix threshold for attachment
                        b.ghost_target_id = getattr(best_target, "id", None)
                else:
                    # Attached to target
                    target_b = next((x for x in balls if getattr(x, "id", None) == target_id), None)
                    if not target_b and hasattr(world, "arena") and hasattr(world.arena, "hazards"):
                        target_b = next((x for x in world.arena.hazards if getattr(x, "id", None) == target_id), None)

                    if target_b:
                        # Snap to target position
                        b.x = getattr(target_b, "x", b.x)
                        b.y = getattr(target_b, "y", b.y)
                        b.vx = 0.0
                        b.vy = 0.0

                        if target_b in balls:
                            # Apply buff/debuff
                            if getattr(b, "team", None) == getattr(target_b, "team", None):
                                # Buff teammate
                                target_b.speed = getattr(target_b, "base_speed", 100.0) * 1.2
                                if hasattr(target_b, "take_damage"):
                                    target_b.hp = min(getattr(target_b, "max_hp", 100.0), getattr(target_b, "hp", 100.0) + 2.0 * delta)
                            else:
                                # Debuff enemy
                                target_b.speed = getattr(target_b, "base_speed", 100.0) * 0.8
                                if hasattr(target_b, "take_damage"):
                                    target_b.take_damage(5.0 * delta)
                                else:
                                    target_b.hp -= 5.0 * delta
                                    if target_b.hp <= 0:
                                        target_b.hp = 0
                                        target_b.alive = False
                        else:
                            # Attached to hazard
                            enemy_near = False
                            for ob in balls:
                                if getattr(ob, "alive", True) and not getattr(ob, "is_ghost", False) and getattr(ob, "ball_type", None) != "spectator":
                                    if getattr(ob, "team", None) != getattr(b, "team", None):
                                        d = (ob.x - b.x)**2 + (ob.y - b.y)**2
                                        if d < 10000.0: # within 100 units
                                            enemy_near = True
                                            break
                            if enemy_near:
                                target_b.active = True
                                target_b.triggered = True
                                b.ghost_target_id = None

    def check_winner(self, world: 'Any', balls: 'List[Any]') -> 'Optional[str]':
        alive = [b for b in balls if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator" and not getattr(b, "is_ghost", False)]
        if not alive:
            return "Draw"

        teams_alive = set(getattr(b, "team", getattr(b, "ball_type", None)) for b in alive)
        if len(teams_alive) == 1:
            return list(teams_alive)[0]

        return None
