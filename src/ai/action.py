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

    def _calculate_avoidance(self, target: Any = None) -> tuple[float, float]:
        ax, ay = 0.0, 0.0
        perception_radius = getattr(self.ball, "perception_radius", 250)

        entities = []
        if hasattr(self.world, "get_nearby_entities"):
            res = self.world.get_nearby_entities(self.ball, perception_radius)
            if isinstance(res, dict):
                entities.extend(res.get("enemies", []))
                entities.extend(res.get("allies", []))
            else:
                entities.extend([e for e in res if getattr(e, "alive", True)])

        ball_radius = getattr(self.ball, "radius", 10.0)

        for e in entities:
            # Skip self
            if getattr(e, "id", None) == getattr(self.ball, "id", None) and getattr(e, "id", None) is not None:
                continue
            if e is target:
                continue

            dx = self.ball.x - e.x
            dy = self.ball.y - e.y
            dist_sq = dx*dx + dy*dy

            if dist_sq > 0.001:
                dist = math.sqrt(dist_sq)
                e_radius = getattr(e, "radius", 10.0)
                avoid_radius = ball_radius + e_radius + 15.0 # buffer zone

                if dist < avoid_radius:
                    # The closer the entity, the stronger the repulsion
                    repel_strength = (avoid_radius - dist) / avoid_radius
                    ax += (dx / dist) * repel_strength * 2.0
                    ay += (dy / dist) * repel_strength * 2.0

        if math.isnan(ax) or math.isinf(ax): ax = 0.0
        if math.isnan(ay) or math.isinf(ay): ay = 0.0

        return ax, ay

    def _flee(self, delta: float) -> None:
        enemies = self._get_enemies()
        if enemies:
            nearest = min(enemies, key=lambda e: (e.x - self.ball.x) ** 2 + (e.y - self.ball.y) ** 2)
            dx, dy = self.ball.x - nearest.x, self.ball.y - nearest.y
            dist = math.sqrt(dx * dx + dy * dy)

            ax, ay = self._calculate_avoidance(nearest)

            if dist > 0.01:
                nx = (dx / dist) + ax
                ny = (dy / dist) + ay

                # Normalize new direction vector
                n_dist = math.sqrt(nx*nx + ny*ny)
                if n_dist > 0.01:
                    nx /= n_dist
                    ny /= n_dist

                speed = getattr(self.ball, "speed", 2.0)
                self.ball.x += nx * speed * delta * 60
                self.ball.y += ny * speed * delta * 60

                if math.isnan(self.ball.x) or math.isinf(self.ball.x): self.ball.x = 0.0
                if math.isnan(self.ball.y) or math.isinf(self.ball.y): self.ball.y = 0.0
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
            attack_range = ball_radius + target_radius + 5

            ax, ay = self._calculate_avoidance(target)

            # Move towards target if not in range
            if dist > attack_range:
                nx = (dx / dist) + ax
                ny = (dy / dist) + ay

                # Normalize new direction vector
                n_dist = math.sqrt(nx*nx + ny*ny)
                if n_dist > 0.01:
                    nx /= n_dist
                    ny /= n_dist

                step = getattr(self.ball, "speed", 2.0) * delta * 60
                self.ball.x += nx * min(step, dist - attack_range)
                self.ball.y += ny * min(step, dist - attack_range)

                if math.isnan(self.ball.x) or math.isinf(self.ball.x): self.ball.x = 0.0
                if math.isnan(self.ball.y) or math.isinf(self.ball.y): self.ball.y = 0.0
            else:
                # Still apply avoidance slightly to prevent overlapping even when at attack range
                if abs(ax) > 0.01 or abs(ay) > 0.01:
                    n_dist = math.sqrt(ax*ax + ay*ay)
                    if n_dist > 0.01:
                        ax /= n_dist
                        ay /= n_dist
                    step = getattr(self.ball, "speed", 2.0) * delta * 60
                    self.ball.x += ax * step * 0.5
                    self.ball.y += ay * step * 0.5

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

            ax, ay = self._calculate_avoidance(nearest)

            ball_radius = getattr(self.ball, "radius", 10.0)
            booster_range = ball_radius + 10

            if dist > booster_range:
                nx = (dx / dist) + ax
                ny = (dy / dist) + ay

                # Normalize new direction vector
                n_dist = math.sqrt(nx*nx + ny*ny)
                if n_dist > 0.01:
                    nx /= n_dist
                    ny /= n_dist

                step = getattr(self.ball, "speed", 2.0) * delta * 60
                self.ball.x += nx * min(step, dist - booster_range)
                self.ball.y += ny * min(step, dist - booster_range)

                if math.isnan(self.ball.x) or math.isinf(self.ball.x): self.ball.x = 0.0
                if math.isnan(self.ball.y) or math.isinf(self.ball.y): self.ball.y = 0.0

            if dist <= booster_range:
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
        if hasattr(self.world, "width") and hasattr(self.world, "height"):
            radius = getattr(self.ball, "radius", 10.0)

            # Additional safety check against NaN values propagated from external sources
            if math.isnan(self.ball.x) or math.isinf(self.ball.x): self.ball.x = self.world.width / 2.0
            if math.isnan(self.ball.y) or math.isinf(self.ball.y): self.ball.y = self.world.height / 2.0

            self.ball.x = max(radius, min(self.world.width - radius, self.ball.x))
            self.ball.y = max(radius, min(self.world.height - radius, self.ball.y))

    def _update_skill_timer(self, delta: float) -> None:
        if hasattr(self.ball, "skill_timer") and self.ball.skill_timer > 0:
            self.ball.skill_timer -= delta
