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

    def _get_allies(self) -> list:
        perception_radius = getattr(self.ball, "perception_radius", 250)
        if hasattr(self.world, "get_nearby_entities"):
            entities = self.world.get_nearby_entities(self.ball, perception_radius)
            if isinstance(entities, dict):
                return entities.get("allies", [])
            else:
                return [e for e in entities if getattr(e, "ball_type", None) == self.ball.ball_type and e != self.ball and getattr(e, "alive", True)]
        return []

    def _apply_boids(self, dx: float, dy: float) -> tuple[float, float]:
        allies = self._get_allies()
        if not allies:
            return dx, dy

        sep_x, sep_y = 0.0, 0.0
        align_x, align_y = 0.0, 0.0
        coh_x, coh_y = 0.0, 0.0

        perception_radius = getattr(self.ball, "perception_radius", 250)
        separation_dist = getattr(self.ball, "radius", 10.0) * 3

        count = 0
        for ally in allies:
            adx = self.ball.x - ally.x
            ady = self.ball.y - ally.y
            dist_sq = adx * adx + ady * ady

            if dist_sq < 0.0001:
                continue

            dist = math.sqrt(dist_sq)

            if dist < perception_radius:
                # Separation
                if dist < separation_dist:
                    sep_x += adx / dist
                    sep_y += ady / dist

                # Alignment
                align_x += getattr(ally, "velocity_x", 0.0)
                align_y += getattr(ally, "velocity_y", 0.0)

                # Cohesion
                coh_x += ally.x
                coh_y += ally.y

                count += 1

        if count > 0:
            # Normalize and apply weights
            # Alignment
            align_x /= count
            align_y /= count
            align_len = math.sqrt(align_x * align_x + align_y * align_y)
            if align_len > 0.01:
                align_x /= align_len
                align_y /= align_len

            # Cohesion
            coh_x /= count
            coh_y /= count
            coh_dx = coh_x - self.ball.x
            coh_dy = coh_y - self.ball.y
            coh_len = math.sqrt(coh_dx * coh_dx + coh_dy * coh_dy)
            if coh_len > 0.01:
                coh_dx /= coh_len
                coh_dy /= coh_len

            # Mix with original intent (dx, dy are already normalized intent vectors or 0)
            # Weights: Intent 1.0, Separation 1.5, Alignment 0.5, Cohesion 0.5
            boid_dx = dx + sep_x * 1.5 + align_x * 0.5 + coh_dx * 0.5
            boid_dy = dy + sep_y * 1.5 + align_y * 0.5 + coh_dy * 0.5

            boid_len = math.sqrt(boid_dx * boid_dx + boid_dy * boid_dy)
            if boid_len > 0.01:
                return boid_dx / boid_len, boid_dy / boid_len

        return dx, dy

    def _apply_movement(self, delta: float, nx: float, ny: float, dist: float, clamp_to_target: bool = True) -> None:
        speed = getattr(self.ball, "speed", 2.0)
        step = speed * delta * 60

        move_dist = min(step, dist) if clamp_to_target else step

        # Apply boids if swarm
        if getattr(self.ball, "ball_type", "") == "swarm":
            nx, ny = self._apply_boids(nx, ny)

        self.ball.x += nx * move_dist
        self.ball.y += ny * move_dist

        # Keep track of velocity for alignment
        self.ball.velocity_x = nx * speed
        self.ball.velocity_y = ny * speed

    def _flee(self, delta: float) -> None:
        enemies = self._get_enemies()
        if enemies:
            nearest = min(enemies, key=lambda e: (e.x - self.ball.x) ** 2 + (e.y - self.ball.y) ** 2)
            dx, dy = self.ball.x - nearest.x, self.ball.y - nearest.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 0.01:
                nx, ny = dx / dist, dy / dist
                self._apply_movement(delta, nx, ny, dist, clamp_to_target=False)
        else:
            self._idle(delta)

    def _attack(self, delta: float) -> None:
        enemies = self._get_enemies()
        if enemies:
            target = min(enemies, key=lambda e: (e.x - self.ball.x) ** 2 + (e.y - self.ball.y) ** 2)
            dx, dy = target.x - self.ball.x, target.y - self.ball.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 0.01:
                nx, ny = dx / dist, dy / dist
                self._apply_movement(delta, nx, ny, dist, clamp_to_target=True)

            # Recalculate distance after movement
            dx_new, dy_new = target.x - self.ball.x, target.y - self.ball.y
            dist_new = math.sqrt(dx_new * dx_new + dy_new * dy_new)

            target_radius = getattr(target, "radius", 10.0)
            ball_radius = getattr(self.ball, "radius", 10.0)

            if dist_new <= ball_radius + target_radius + 5.01:
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
                self._apply_movement(delta, nx, ny, dist, clamp_to_target=True)

            # Recalculate distance after movement
            dx_new, dy_new = nearest.x - self.ball.x, nearest.y - self.ball.y
            dist_new = math.sqrt(dx_new * dx_new + dy_new * dy_new)

            ball_radius = getattr(self.ball, "radius", 10.0)
            if dist_new <= ball_radius + 10.01:
                if hasattr(self.world, "_collect_booster"):
                    self.world._collect_booster(self.ball, nearest)
        else:
            self._idle(delta)

    def _use_skill(self) -> None:
        if hasattr(self.ball, "use_skill"):
            self.ball.use_skill()

    def _idle(self, delta: float) -> None:
        speed = getattr(self.ball, "speed", 2.0)
        nx = random.uniform(-1, 1)
        ny = random.uniform(-1, 1)
        length = math.sqrt(nx * nx + ny * ny)
        if length > 0.01:
            nx /= length
            ny /= length

        # Idle movement dist is typically small
        dist = speed * 0.3 * delta * 60
        self._apply_movement(delta, nx, ny, dist, clamp_to_target=True)

    def _clamp_position(self) -> None:
        if hasattr(self.world, "width") and hasattr(self.world, "height"):
            radius = getattr(self.ball, "radius", 10.0)
            self.ball.x = max(radius, min(self.world.width - radius, self.ball.x))
            self.ball.y = max(radius, min(self.world.height - radius, self.ball.y))

    def _update_skill_timer(self, delta: float) -> None:
        if hasattr(self.ball, "skill_timer") and self.ball.skill_timer > 0:
            self.ball.skill_timer -= delta
