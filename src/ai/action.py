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

    def _apply_movement(self, dx: float, dy: float, dist: float, delta: float, clamp_to_target: bool = True) -> None:
        """
        Handles basic movement and obstacle avoidance logic by calculating repulsive forces.
        """
        if dist <= 0.01:
            return

        nx, ny = dx / dist, dy / dist

        # Obstacle avoidance
        repulse_x, repulse_y = 0.0, 0.0
        perception_radius = getattr(self.ball, "perception_radius", 250)
        ball_radius = getattr(self.ball, "radius", 10.0)

        if hasattr(self.world, "get_nearby_entities"):
            entities_dict = self.world.get_nearby_entities(self.ball, perception_radius)
            all_entities = []
            if isinstance(entities_dict, dict):
                for k, v in entities_dict.items():
                    if k != "boosters" and k != "traps":
                        all_entities.extend(v)
            else:
                all_entities = entities_dict

            for entity in all_entities:
                if entity is self.ball:
                    continue
                entity_radius = getattr(entity, "radius", 10.0)
                edx = self.ball.x - entity.x
                edy = self.ball.y - entity.y
                edist = math.sqrt(edx*edx + edy*edy)

                safety_threshold = ball_radius + entity_radius + 5.0
                if edist > 0.01 and edist < safety_threshold:
                    force = 1.0 - (edist / safety_threshold)
                    repulse_x += (edx / edist) * force
                    repulse_y += (edy / edist) * force

        # Combine movement and repulsion
        fx = nx + repulse_x
        fy = ny + repulse_y
        fdist = math.sqrt(fx*fx + fy*fy)

        if fdist > 0.01:
            nx, ny = fx / fdist, fy / fdist

        speed = getattr(self.ball, "speed", 2.0)
        step = speed * delta * 60.0

        if clamp_to_target:
            self.ball.x += nx * min(step, dist)
            self.ball.y += ny * min(step, dist)
        else:
            self.ball.x += nx * step
            self.ball.y += ny * step


    def _flee(self, delta: float) -> None:
        enemies = self._get_enemies()
        if enemies:
            nearest = min(enemies, key=lambda e: (e.x - self.ball.x) ** 2 + (e.y - self.ball.y) ** 2)
            dx, dy = self.ball.x - nearest.x, self.ball.y - nearest.y
            dist = math.sqrt(dx * dx + dy * dy)
            self._apply_movement(dx, dy, dist, delta, clamp_to_target=False)
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
                self._apply_movement(dx, dy, dist, delta, clamp_to_target=True)

            # Recalculate distance after movement
            dx, dy = target.x - self.ball.x, target.y - self.ball.y
            dist_new = math.sqrt(dx * dx + dy * dy)

            if dist_new <= attack_range + 0.01:
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
                self._apply_movement(dx, dy, dist, delta, clamp_to_target=True)

            # Recalculate distance
            dx, dy = nearest.x - self.ball.x, nearest.y - self.ball.y
            dist_new = math.sqrt(dx * dx + dy * dy)

            if dist_new <= collect_range + 0.01:
                if hasattr(self.world, "_collect_booster"):
                    self.world._collect_booster(self.ball, nearest)
        else:
            self._idle(delta)

    def _use_skill(self) -> None:
        skill_timer = getattr(self.ball, "skill_timer", 0.0)
        if skill_timer <= 0:
            if hasattr(self.ball, "use_skill"):
                self.ball.use_skill()
            if hasattr(self.ball, "skill_cooldown"):
                self.ball.skill_timer = self.ball.skill_cooldown

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
