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

    def _calculate_steering(self, target_x: float, target_y: float, target_ent: Any = None, flee: bool = False) -> tuple[float, float]:
        dx = target_x - self.ball.x
        dy = target_y - self.ball.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist > 0:
            nx = dx / dist
            ny = dy / dist
            if flee:
                nx = -nx
                ny = -ny
        else:
            nx, ny = 0.0, 0.0

        perception_radius = getattr(self.ball, "perception_radius", 250)
        entities = []
        if hasattr(self.world, "get_nearby_entities"):
            entities_dict = self.world.get_nearby_entities(self.ball, perception_radius)
            if isinstance(entities_dict, dict):
                entities.extend(entities_dict.get("enemies", []))
                entities.extend(entities_dict.get("allies", []))
                entities.extend(entities_dict.get("boosters", []))
                entities.extend(entities_dict.get("traps", []))
            elif isinstance(entities_dict, list):
                entities.extend(entities_dict)

        repulse_x = 0.0
        repulse_y = 0.0

        for e in entities:
            if e is target_ent or e is self.ball:
                continue

            ex = getattr(e, "x", None)
            ey = getattr(e, "y", None)
            if ex is None or ey is None:
                continue

            if math.isnan(ex) or math.isnan(ey):
                continue

            edx = self.ball.x - ex
            edy = self.ball.y - ey
            edist = math.sqrt(edx * edx + edy * edy)

            avoid_radius = getattr(self.ball, "radius", 10.0) + getattr(e, "radius", 10.0) + 10.0
            if edist > 0 and edist < avoid_radius:
                repulse_x += (edx / edist) * (avoid_radius - edist)
                repulse_y += (edy / edist) * (avoid_radius - edist)
            elif edist == 0:
                repulse_x += random.uniform(-1, 1)
                repulse_y += random.uniform(-1, 1)

        combined_x = nx + repulse_x * 0.5
        combined_y = ny + repulse_y * 0.5

        cdist = math.sqrt(combined_x * combined_x + combined_y * combined_y)
        if cdist > 0:
            combined_x /= cdist
            combined_y /= cdist
        else:
            combined_x, combined_y = 0.0, 0.0

        if math.isnan(combined_x) or math.isinf(combined_x):
            combined_x = 0.0
        if math.isnan(combined_y) or math.isinf(combined_y):
            combined_y = 0.0

        return combined_x, combined_y

    def _flee(self, delta: float) -> None:
        enemies = self._get_enemies()
        if enemies:
            nearest = min(enemies, key=lambda e: (e.x - self.ball.x) ** 2 + (e.y - self.ball.y) ** 2)
            nx, ny = self._calculate_steering(nearest.x, nearest.y, nearest, flee=True)

            step = getattr(self.ball, "speed", 2.0) * delta * 60
            self.ball.x += nx * step
            self.ball.y += ny * step
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

            if dist > attack_range:
                nx, ny = self._calculate_steering(target.x, target.y, target, flee=False)
                step = getattr(self.ball, "speed", 2.0) * delta * 60

                # Prevent overshooting the attack range
                move_dist = min(step, dist - attack_range)
                self.ball.x += nx * move_dist
                self.ball.y += ny * move_dist

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

            ball_radius = getattr(self.ball, "radius", 10.0)
            collect_range = ball_radius + 10.0

            if dist > 0.01:
                nx, ny = self._calculate_steering(nearest.x, nearest.y, nearest, flee=False)
                step = getattr(self.ball, "speed", 2.0) * delta * 60
                self.ball.x += nx * min(step, dist)
                self.ball.y += ny * min(step, dist)

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
        if hasattr(self.world, "width") and hasattr(self.world, "height"):
            if math.isnan(self.ball.x) or math.isinf(self.ball.x):
                self.ball.x = self.world.width / 2.0
            if math.isnan(self.ball.y) or math.isinf(self.ball.y):
                self.ball.y = self.world.height / 2.0

            radius = getattr(self.ball, "radius", 10.0)
            self.ball.x = max(radius, min(self.world.width - radius, self.ball.x))
            self.ball.y = max(radius, min(self.world.height - radius, self.ball.y))

    def _update_skill_timer(self, delta: float) -> None:
        if hasattr(self.ball, "skill_timer") and self.ball.skill_timer > 0:
            self.ball.skill_timer -= delta
