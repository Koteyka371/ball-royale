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

    def _apply_movement(self, target_dx: float, target_dy: float, speed_multiplier: float, delta: float, clamp_to_target: bool = True) -> None:
        if math.isnan(target_dx) or math.isnan(target_dy) or math.isinf(target_dx) or math.isinf(target_dy):
            return

        dist = math.sqrt(target_dx * target_dx + target_dy * target_dy)
        if dist < 0.001:
            return

        nx = target_dx / dist
        ny = target_dy / dist

        # Simple obstacle avoidance (repulsive force)
        repulse_x, repulse_y = 0.0, 0.0
        ball_radius = getattr(self.ball, "radius", 10.0)
        perception_radius = getattr(self.ball, "perception_radius", 250)

        if hasattr(self.world, "get_nearby_entities"):
            entities_dict = self.world.get_nearby_entities(self.ball, perception_radius)
            all_entities = []
            if isinstance(entities_dict, dict):
                all_entities.extend(entities_dict.get("allies", []))
                all_entities.extend(entities_dict.get("enemies", []))
            elif isinstance(entities_dict, list):
                all_entities = [e for e in entities_dict if getattr(e, "alive", True)]

            for e in all_entities:
                if e is self.ball:
                    continue
                edx, edy = self.ball.x - e.x, self.ball.y - e.y
                edist = math.sqrt(edx * edx + edy * edy)
                eradius = getattr(e, "radius", 10.0)
                safety_threshold = ball_radius + eradius + 5.0

                if 0.001 < edist < safety_threshold:
                    force = (safety_threshold - edist) / safety_threshold
                    repulse_x += (edx / edist) * force
                    repulse_y += (edy / edist) * force

        # Combine forces
        final_nx = nx * speed_multiplier + repulse_x
        final_ny = ny * speed_multiplier + repulse_y

        final_dist = math.sqrt(final_nx * final_nx + final_ny * final_ny)
        if final_dist > 0.001:
            final_nx /= final_dist
            final_ny /= final_dist

        speed = getattr(self.ball, "speed", 2.0)
        step = speed * delta * 60

        if clamp_to_target and speed_multiplier > 0:
            step = min(step, dist)

        self.ball.x += final_nx * step
        self.ball.y += final_ny * step

    def _flee(self, delta: float) -> None:
        enemies = self._get_enemies()
        if enemies:
            nearest = min(enemies, key=lambda e: (e.x - self.ball.x) ** 2 + (e.y - self.ball.y) ** 2)
            dx, dy = self.ball.x - nearest.x, self.ball.y - nearest.y
            self._apply_movement(dx, dy, 1.0, delta, clamp_to_target=False)
        else:
            self._idle(delta)

    def _attack(self, delta: float) -> None:
        enemies = self._get_enemies()
        if enemies:
            target = min(enemies, key=lambda e: (e.x - self.ball.x) ** 2 + (e.y - self.ball.y) ** 2)
            dx, dy = target.x - self.ball.x, target.y - self.ball.y

            target_radius = getattr(target, "radius", 10.0)
            ball_radius = getattr(self.ball, "radius", 10.0)
            target_range = ball_radius + target_radius + 5.0

            dist = math.sqrt(dx * dx + dy * dy)
            if dist > target_range:
                self._apply_movement(dx, dy, 1.0, delta, clamp_to_target=True)

                # Recalculate distance after movement
                dx, dy = target.x - self.ball.x, target.y - self.ball.y
                dist = math.sqrt(dx * dx + dy * dy)

            if dist <= target_range + 0.01:
                if hasattr(self.world, "_deal_damage"):
                    self.world._deal_damage(self.ball, target)
        else:
            self._idle(delta)

    def _defend(self, delta: float) -> None:
        self._idle(delta * 0.5)

    def _collect_booster(self, delta: float) -> None:
        boosters = self._get_boosters()
        if boosters:
            nearest = min(boosters, key=lambda b: (b.x - self.ball.x) ** 2 + (b.y - self.ball.y) ** 2)
            dx, dy = nearest.x - self.ball.x, nearest.y - self.ball.y

            ball_radius = getattr(self.ball, "radius", 10.0)
            target_range = ball_radius + 10.0

            dist = math.sqrt(dx * dx + dy * dy)
            if dist > target_range:
                self._apply_movement(dx, dy, 1.0, delta, clamp_to_target=True)

                # Recalculate distance after movement
                dx, dy = nearest.x - self.ball.x, nearest.y - self.ball.y
                dist = math.sqrt(dx * dx + dy * dy)

            if dist <= target_range + 0.01:
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
        if hasattr(self.world, "width") and hasattr(self.world, "height"):
            radius = getattr(self.ball, "radius", 10.0)
            self.ball.x = max(radius, min(self.world.width - radius, self.ball.x))
            self.ball.y = max(radius, min(self.world.height - radius, self.ball.y))

    def _update_skill_timer(self, delta: float) -> None:
        if hasattr(self.ball, "skill_timer") and self.ball.skill_timer > 0:
            self.ball.skill_timer -= delta
