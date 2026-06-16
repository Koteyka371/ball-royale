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
                return [e for e in entities if getattr(e, "ball_type", None) != getattr(self.ball, "ball_type", None) and getattr(e, "alive", True) and e != self.ball]
        return []

    def _get_allies(self) -> list:
        perception_radius = getattr(self.ball, "perception_radius", 250)
        if hasattr(self.world, "get_nearby_entities"):
            entities = self.world.get_nearby_entities(self.ball, perception_radius)
            if isinstance(entities, dict):
                return entities.get("allies", [])
            else:
                return [e for e in entities if getattr(e, "ball_type", None) == getattr(self.ball, "ball_type", None) and getattr(e, "alive", True) and e != self.ball]
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

    def _flee(self, delta: float) -> None:
        enemies = self._get_enemies()
        if not enemies:
            self._idle(delta)
            return

        nearest_enemy = min(enemies, key=lambda e: (e.x - self.ball.x) ** 2 + (e.y - self.ball.y) ** 2)
        dx, dy = self.ball.x - nearest_enemy.x, self.ball.y - nearest_enemy.y
        dist = math.sqrt(dx * dx + dy * dy)

        perception_radius = getattr(self.ball, "perception_radius", 250.0)
        safe_distance = perception_radius * 0.8

        if dist > safe_distance:
            # We are safe enough, stop fleeing
            self._idle(delta * 0.5)
            return

        ex, ey = 0.0, 0.0
        if dist > 0.01:
            ex, ey = dx / dist, dy / dist

        allies = self._get_allies()
        ax, ay = 0.0, 0.0
        if allies:
            nearest_ally = min(allies, key=lambda a: (a.x - self.ball.x) ** 2 + (a.y - self.ball.y) ** 2)
            adx, ady = nearest_ally.x - self.ball.x, nearest_ally.y - self.ball.y
            adist = math.sqrt(adx * adx + ady * ady)
            if adist > 0.01:
                ax, ay = adx / adist, ady / adist

        cx, cy = 0.0, 0.0
        if hasattr(self.world, "width") and hasattr(self.world, "height"):
            center_x, center_y = self.world.width / 2.0, self.world.height / 2.0
            cdx, cdy = center_x - self.ball.x, center_y - self.ball.y
            cdist = math.sqrt(cdx * cdx + cdy * cdy)
            if cdist > 0.01:
                cx, cy = cdx / cdist, cdy / cdist

        # Weights: threat avoidance (1.0), move to ally (0.5), move to center (0.2)
        vx = ex * 1.0 + ax * 0.5 + cx * 0.2
        vy = ey * 1.0 + ay * 0.5 + cy * 0.2

        if math.isnan(vx) or math.isinf(vx): vx = 0.0
        if math.isnan(vy) or math.isinf(vy): vy = 0.0

        v_dist = math.sqrt(vx * vx + vy * vy)
        if v_dist > 0.01:
            vx, vy = vx / v_dist, vy / v_dist
        else:
            # Fallback to pure away-from-enemy if combined vector is zero
            vx, vy = ex, ey

        # 1.5x speed boost when fleeing
        speed = getattr(self.ball, "speed", 2.0) * 1.5
        self.ball.x += vx * speed * delta * 60
        self.ball.y += vy * speed * delta * 60

    def _attack(self, delta: float) -> None:
        enemies = self._get_enemies()
        if enemies:
            target = min(enemies, key=lambda e: (e.x - self.ball.x) ** 2 + (e.y - self.ball.y) ** 2)
            dx, dy = target.x - self.ball.x, target.y - self.ball.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 0.01:
                nx, ny = dx / dist, dy / dist
                step = getattr(self.ball, "speed", 2.0) * delta * 60
                self.ball.x += nx * min(step, dist)
                self.ball.y += ny * min(step, dist)

            target_radius = getattr(target, "radius", 10.0)
            ball_radius = getattr(self.ball, "radius", 10.0)

            if dist <= ball_radius + target_radius + 5:
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
            if dist > 0.01:
                nx, ny = dx / dist, dy / dist
                step = getattr(self.ball, "speed", 2.0) * delta * 60
                self.ball.x += nx * min(step, dist)
                self.ball.y += ny * min(step, dist)

            ball_radius = getattr(self.ball, "radius", 10.0)
            if dist <= ball_radius + 10:
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
            self.ball.x = max(radius, min(self.world.width - radius, self.ball.x))
            self.ball.y = max(radius, min(self.world.height - radius, self.ball.y))

    def _update_skill_timer(self, delta: float) -> None:
        if hasattr(self.ball, "skill_timer") and self.ball.skill_timer > 0:
            self.ball.skill_timer -= delta
