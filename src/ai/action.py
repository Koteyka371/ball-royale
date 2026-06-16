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

    def _calculate_repulsion(self, exclude_target: Any = None) -> tuple[float, float]:
        """Calculates a repulsion vector from obstacles (enemies, allies, traps)."""
        rx, ry = 0.0, 0.0
        perception_radius = getattr(self.ball, "perception_radius", 250)

        if hasattr(self.world, "get_nearby_entities"):
            entities = self.world.get_nearby_entities(self.ball, perception_radius)
            if isinstance(entities, dict):
                obstacles = entities.get("enemies", []) + entities.get("allies", []) + entities.get("traps", [])

                for obs in obstacles:
                    if obs == exclude_target:
                        continue

                    dx = self.ball.x - obs.x
                    dy = self.ball.y - obs.y
                    dist_sq = dx*dx + dy*dy
                    if dist_sq > 0.0001:
                        dist = math.sqrt(dist_sq)
                        # Repel stronger when closer
                        weight = 1.0 / dist
                        rx += (dx / dist) * weight
                        ry += (dy / dist) * weight

        if math.isnan(rx) or math.isinf(rx): rx = 0.0
        if math.isnan(ry) or math.isinf(ry): ry = 0.0
        return rx, ry

    def _flee(self, delta: float) -> None:
        enemies = self._get_enemies()
        if enemies:
            nearest = min(enemies, key=lambda e: (e.x - self.ball.x) ** 2 + (e.y - self.ball.y) ** 2)
            dx, dy = self.ball.x - nearest.x, self.ball.y - nearest.y
            dist = math.sqrt(dx * dx + dy * dy)

            rx, ry = self._calculate_repulsion()

            if dist > 0.01:
                dir_x = (dx / dist) + rx * 20.0
                dir_y = (dy / dist) + ry * 20.0

                dir_dist = math.sqrt(dir_x*dir_x + dir_y*dir_y)
                if dir_dist > 0.0001:
                    dir_x /= dir_dist
                    dir_y /= dir_dist

                self.ball.x += dir_x * getattr(self.ball, "speed", 2.0) * delta * 60
                self.ball.y += dir_y * getattr(self.ball, "speed", 2.0) * delta * 60
        else:
            self._idle(delta)

    def _attack(self, delta: float) -> None:
        enemies = self._get_enemies()
        if enemies:
            target = min(enemies, key=lambda e: (e.x - self.ball.x) ** 2 + (e.y - self.ball.y) ** 2)
            dx, dy = target.x - self.ball.x, target.y - self.ball.y
            dist = math.sqrt(dx * dx + dy * dy)

            rx, ry = self._calculate_repulsion(target)

            target_radius = getattr(target, "radius", 10.0)
            ball_radius = getattr(self.ball, "radius", 10.0)
            attack_range = ball_radius + target_radius + 5

            if dist > attack_range:
                dir_x = (dx / dist) + rx * 10.0
                dir_y = (dy / dist) + ry * 10.0

                dir_dist = math.sqrt(dir_x*dir_x + dir_y*dir_y)
                if dir_dist > 0.0001:
                    dir_x /= dir_dist
                    dir_y /= dir_dist

                step = getattr(self.ball, "speed", 2.0) * delta * 60
                move_dist = min(step, dist - attack_range + 2) # Don't overshoot

                self.ball.x += dir_x * move_dist
                self.ball.y += dir_y * move_dist

            if dist <= attack_range:
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

            rx, ry = self._calculate_repulsion(nearest)

            ball_radius = getattr(self.ball, "radius", 10.0)
            collect_range = ball_radius + 10

            if dist > collect_range:
                dir_x = (dx / dist) + rx * 10.0
                dir_y = (dy / dist) + ry * 10.0

                dir_dist = math.sqrt(dir_x*dir_x + dir_y*dir_y)
                if dir_dist > 0.0001:
                    dir_x /= dir_dist
                    dir_y /= dir_dist

                step = getattr(self.ball, "speed", 2.0) * delta * 60
                move_dist = min(step, dist - collect_range + 2)

                self.ball.x += dir_x * move_dist
                self.ball.y += dir_y * move_dist

            if dist <= collect_range:
                if hasattr(self.world, "_collect_booster"):
                    self.world._collect_booster(self.ball, nearest)
        else:
            self._idle(delta)

    def _use_skill(self) -> None:
        if hasattr(self.ball, "use_skill"):
            self.ball.use_skill()

    def _idle(self, delta: float) -> None:
        speed = getattr(self.ball, "speed", 2.0)
        self.ball.x += random.uniform(-1, 1) * speed * 0.3
        self.ball.y += random.uniform(-1, 1) * speed * 0.3

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
