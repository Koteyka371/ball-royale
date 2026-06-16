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

    def _apply_movement(self, dx: float, dy: float, dist: float, delta: float, clamp_to_target: bool = True, target: Any = None) -> None:
        if dist <= 0.01:
            return

        nx, ny = dx / dist, dy / dist

        # Pathfinding / Obstacle Avoidance
        perception_radius = getattr(self.ball, "perception_radius", 250)
        nearby_entities = []
        if hasattr(self.world, "get_nearby_entities"):
            entities = self.world.get_nearby_entities(self.ball, perception_radius)
            if isinstance(entities, dict):
                nearby_entities.extend(entities.get("enemies", []))
                nearby_entities.extend(entities.get("allies", []))
                nearby_entities.extend(entities.get("traps", []))
            else:
                nearby_entities = list(entities)

        ball_radius = getattr(self.ball, "radius", 10.0)
        repulsion_x, repulsion_y = 0.0, 0.0

        for e in nearby_entities:
            if e is target or e is self.ball:
                continue
            if not getattr(e, "alive", True):
                continue

            e_radius = getattr(e, "radius", 10.0)
            threshold = ball_radius + e_radius + 5.0

            ex, ey = getattr(e, "x", 0.0), getattr(e, "y", 0.0)
            edx, edy = self.ball.x - ex, self.ball.y - ey
            edist = math.sqrt(edx*edx + edy*edy)

            if 0 < edist < threshold:
                force = (threshold - edist) / threshold
                repulsion_x += (edx / edist) * force
                repulsion_y += (edy / edist) * force

        nx += repulsion_x
        ny += repulsion_y

        # Re-normalize
        ndist = math.sqrt(nx*nx + ny*ny)
        if ndist > 0.01:
            nx /= ndist
            ny /= ndist

        speed = getattr(self.ball, "speed", 2.0)
        step = speed * delta * 60

        if clamp_to_target:
            move_dist = min(step, dist)
        else:
            move_dist = step

        self.ball.x += nx * move_dist
        self.ball.y += ny * move_dist

    def _flee(self, delta: float) -> None:
        enemies = self._get_enemies()
        if enemies:
            nearest = min(enemies, key=lambda e: (e.x - self.ball.x) ** 2 + (e.y - self.ball.y) ** 2)
            dx, dy = self.ball.x - nearest.x, self.ball.y - nearest.y
            dist = math.sqrt(dx * dx + dy * dy)
            self._apply_movement(dx, dy, dist, delta, clamp_to_target=False, target=nearest)
        else:
            self._idle(delta)

    def _attack(self, delta: float) -> None:
        enemies = self._get_enemies()
        if enemies:
            target = min(enemies, key=lambda e: (e.x - self.ball.x) ** 2 + (e.y - self.ball.y) ** 2)
            dx, dy = target.x - self.ball.x, target.y - self.ball.y
            dist = math.sqrt(dx * dx + dy * dy)

            self._apply_movement(dx, dy, dist, delta, clamp_to_target=True, target=target)

            # Recalculate distance after moving
            dx_new, dy_new = target.x - self.ball.x, target.y - self.ball.y
            dist_new = math.sqrt(dx_new * dx_new + dy_new * dy_new)

            target_radius = getattr(target, "radius", 10.0)
            ball_radius = getattr(self.ball, "radius", 10.0)

            if dist_new <= ball_radius + target_radius + 5:
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

            self._apply_movement(dx, dy, dist, delta, clamp_to_target=True, target=nearest)

            # Recalculate distance after moving
            dx_new, dy_new = nearest.x - self.ball.x, nearest.y - self.ball.y
            dist_new = math.sqrt(dx_new * dx_new + dy_new * dy_new)

            ball_radius = getattr(self.ball, "radius", 10.0)
            if dist_new <= ball_radius + 10:
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
        self.ball.x += random.uniform(-1, 1) * speed * 0.3
        self.ball.y += random.uniform(-1, 1) * speed * 0.3

    def _clamp_position(self) -> None:
        if math.isnan(self.ball.x) or math.isinf(self.ball.x):
            self.ball.x = getattr(self.ball, "radius", 10.0)
        if math.isnan(self.ball.y) or math.isinf(self.ball.y):
            self.ball.y = getattr(self.ball, "radius", 10.0)

        if hasattr(self.world, "width") and hasattr(self.world, "height"):
            radius = getattr(self.ball, "radius", 10.0)
            self.ball.x = max(radius, min(self.world.width - radius, self.ball.x))
            self.ball.y = max(radius, min(self.world.height - radius, self.ball.y))

    def _update_skill_timer(self, delta: float) -> None:
        if hasattr(self.ball, "skill_timer") and self.ball.skill_timer > 0:
            self.ball.skill_timer -= delta
