from typing import Any
import math
import random

class Action:
    """
    Action execution system.
    Executes the chosen behavior (strategy) by interacting with the ball.
    Handles movement, pathfinding, timing, and cooldowns.
    """
    def __init__(self, ball: Any, world: Any):
        self.ball = ball
        self.world = world

    def execute(self, strategy: str, delta: float) -> None:
        """
        Executes the chosen strategy.
        """
        self.ball.current_action = strategy

        if strategy == "flee":
            self._flee(delta)
        elif strategy in ("attack", "chase"):
            self._attack(delta)
        elif strategy == "defend":
            self._defend(delta)
        elif strategy in ("opportunistic", "collect_booster", "collect booster"):
            self._collect_booster(delta)
        elif strategy in ("use_skill", "use skill"):
            self._use_skill()
        else:
            self._idle(delta)

        self._clamp_position()
        self._update_skill_timer(delta)

    def _get_enemies(self) -> list:
        perception_radius = getattr(self.ball, "perception_radius", 250)
        if hasattr(self.world, "get_nearby_entities"):
            entities = self.world.get_nearby_entities(self.ball, perception_radius)
            if isinstance(entities, dict):
                return entities.get("enemies", [])
            else:
                return [e for e in entities if getattr(e, "ball_type", None) != self.ball.ball_type and getattr(e, "alive", True)]
        return []

    def _get_boosters(self) -> list:
        perception_radius = getattr(self.ball, "perception_radius", 250)
        if hasattr(self.world, "get_nearby_entities"):
            entities = self.world.get_nearby_entities(self.ball, perception_radius)
            if isinstance(entities, dict):
                return entities.get("boosters", [])
        # Fallback
        boosters = []
        if hasattr(self.world, "boosters"):
            for b in self.world.boosters:
                if getattr(b, "active", False):
                    dx = b.x - self.ball.x
                    dy = b.y - self.ball.y
                    if math.sqrt(dx*dx + dy*dy) <= perception_radius:
                        boosters.append(b)
        return boosters

    def _apply_movement(self, nx: float, ny: float, step: float, dist: float, is_fleeing: bool = False, target: Any = None) -> None:
        """
        Applies movement vector with obstacle avoidance.
        """
        if math.isnan(nx) or math.isnan(ny) or math.isinf(nx) or math.isinf(ny):
            return

        final_nx = nx
        final_ny = ny

        # Simple obstacle avoidance using repulsive forces from nearby entities
        perception_radius = getattr(self.ball, "perception_radius", 250)
        if hasattr(self.world, "get_nearby_entities"):
            entities_dict = self.world.get_nearby_entities(self.ball, perception_radius)
            all_entities = []
            if isinstance(entities_dict, dict):
                all_entities.extend(entities_dict.get("enemies", []))
                all_entities.extend(entities_dict.get("allies", []))

            ball_radius = getattr(self.ball, "radius", 10.0)

            repulsive_x = 0.0
            repulsive_y = 0.0

            for ent in all_entities:
                if ent == self.ball or ent == target:
                    continue

                ex = getattr(ent, "x", 0)
                ey = getattr(ent, "y", 0)
                eradius = getattr(ent, "radius", 10.0)

                dx = self.ball.x - ex
                dy = self.ball.y - ey
                d = math.sqrt(dx*dx + dy*dy)

                safety_threshold = ball_radius + eradius + 5.0

                if 0.01 < d < safety_threshold:
                    force = (safety_threshold - d) / safety_threshold
                    repulsive_x += (dx / d) * force
                    repulsive_y += (dy / d) * force

            if abs(repulsive_x) > 0.01 or abs(repulsive_y) > 0.01:
                final_nx += repulsive_x
                final_ny += repulsive_y

                # Re-normalize
                m = math.sqrt(final_nx*final_nx + final_ny*final_ny)
                if m > 0.01:
                    final_nx /= m
                    final_ny /= m

        if math.isnan(final_nx) or math.isnan(final_ny) or math.isinf(final_nx) or math.isinf(final_ny):
            return

        if is_fleeing:
            self.ball.x += final_nx * step
            self.ball.y += final_ny * step
        else:
            self.ball.x += final_nx * min(step, dist)
            self.ball.y += final_ny * min(step, dist)

    def _flee(self, delta: float) -> None:
        enemies = self._get_enemies()
        if enemies:
            nearest = min(enemies, key=lambda e: (e.x - self.ball.x) ** 2 + (e.y - self.ball.y) ** 2)
            dx, dy = self.ball.x - nearest.x, self.ball.y - nearest.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 0.01:
                nx, ny = dx / dist, dy / dist
                step = getattr(self.ball, "speed", 2.0) * delta * 60
                self._apply_movement(nx, ny, step, dist, is_fleeing=True, target=nearest)
        else:
            self._idle(delta)

    def _attack(self, delta: float) -> None:
        enemies = self._get_enemies()
        if enemies:
            target = min(enemies, key=lambda e: (e.x - self.ball.x) ** 2 + (e.y - self.ball.y) ** 2)
            dx, dy = target.x - self.ball.x, target.y - self.ball.y
            dist = math.sqrt(dx * dx + dy * dy)

            target_radius = getattr(target, "radius", 10.0)
            ball_radius = getattr(self.ball, "radius", 10.0)
            attack_range = ball_radius + target_radius + 5.0

            if dist > attack_range:
                nx, ny = dx / dist, dy / dist
                step = getattr(self.ball, "speed", 2.0) * delta * 60
                self._apply_movement(nx, ny, step, dist, is_fleeing=False, target=target)

                # Recompute distance after movement
                dx, dy = target.x - self.ball.x, target.y - self.ball.y
                dist = math.sqrt(dx * dx + dy * dy)

            if dist <= attack_range + 0.01:
                if hasattr(self.world, "_deal_damage"):
                    self.world._deal_damage(self.ball, target)
        else:
            self._idle(delta)

    def _defend(self, delta: float) -> None:
        # Defend might mean moving less or using shield. For now, small random moves or static
        self._idle(delta * 0.5)

    def _collect_booster(self, delta: float) -> None:
        boosters = self._get_boosters()
        if boosters:
            nearest = min(boosters, key=lambda b: (b.x - self.ball.x) ** 2 + (b.y - self.ball.y) ** 2)
            dx, dy = nearest.x - self.ball.x, nearest.y - self.ball.y
            dist = math.sqrt(dx * dx + dy * dy)

            ball_radius = getattr(self.ball, "radius", 10.0)
            collect_range = ball_radius + 10.0

            if dist > collect_range:
                nx, ny = dx / dist, dy / dist
                step = getattr(self.ball, "speed", 2.0) * delta * 60
                self._apply_movement(nx, ny, step, dist, is_fleeing=False, target=nearest)

                # Recompute distance
                dx, dy = nearest.x - self.ball.x, nearest.y - self.ball.y
                dist = math.sqrt(dx * dx + dy * dy)

            if dist <= collect_range + 0.01:
                if hasattr(self.world, "_collect_booster"):
                    self.world._collect_booster(self.ball, nearest)
        else:
            self._idle(delta)

    def _use_skill(self) -> None:
        skill_timer = getattr(self.ball, "skill_timer", 0.0)
        if skill_timer <= 0:
            if hasattr(self.ball, "use_skill"):
                self.ball.use_skill()
                skill_cooldown = getattr(self.ball, "skill_cooldown", 5.0)
                self.ball.skill_timer = skill_cooldown

    def _idle(self, delta: float) -> None:
        speed = getattr(self.ball, "speed", 2.0)
        nx = random.uniform(-1, 1)
        ny = random.uniform(-1, 1)
        m = math.sqrt(nx*nx + ny*ny)
        if m > 0.01:
            nx /= m
            ny /= m
        else:
            nx, ny = 0.0, 0.0
        step = speed * 0.3
        self._apply_movement(nx, ny, step, step, is_fleeing=True) # use is_fleeing to not clamp to "dist"

    def _clamp_position(self) -> None:
        if math.isnan(self.ball.x) or math.isinf(self.ball.x):
            self.ball.x = 0.0
        if math.isnan(self.ball.y) or math.isinf(self.ball.y):
            self.ball.y = 0.0

        if hasattr(self.world, "width") and hasattr(self.world, "height"):
            radius = getattr(self.ball, "radius", 10.0)
            self.ball.x = max(radius, min(self.world.width - radius, self.ball.x))
            self.ball.y = max(radius, min(self.world.height - radius, self.ball.y))

    def _update_skill_timer(self, delta: float) -> None:
        if hasattr(self.ball, "skill_timer") and self.ball.skill_timer > 0:
            self.ball.skill_timer -= delta
