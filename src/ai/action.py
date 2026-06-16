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
        self.ball.team_message = None  # Clear previous message

        # Emit messages based on state or strategy
        hp_percent = 1.0
        if hasattr(self.ball, "get_hp_percent"):
            hp_percent = self.ball.get_hp_percent()
        elif hasattr(self.ball, "hp") and hasattr(self.ball, "max_hp"):
            hp_percent = float(self.ball.hp) / float(self.ball.max_hp)

        personality = getattr(self.ball, "personality", "idle")

        if hp_percent < 0.3:
            self.ball.team_message = {"type": "request_help", "x": self.ball.x, "y": self.ball.y}
        elif personality == "healer":
            self.ball.team_message = {"type": "wounded_call", "x": self.ball.x, "y": self.ball.y}
        elif strategy == "defend" and personality == "tank":
            self.ball.team_message = {"type": "hold_position", "x": self.ball.x, "y": self.ball.y}

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


    def _apply_obstacle_avoidance(self, nx: float, ny: float, target: Any = None) -> tuple[float, float]:
        """Applies a repulsive force from nearby entities to avoid collisions."""
        all_entities = []
        perception_radius = getattr(self.ball, "perception_radius", 250)

        if hasattr(self.world, "get_nearby_entities"):
            entities = self.world.get_nearby_entities(self.ball, perception_radius)
            if isinstance(entities, dict):
                for key in ["enemies", "allies"]:
                    all_entities.extend(entities.get(key, []))
            else:
                all_entities = [e for e in entities if getattr(e, "alive", True) and e != self.ball]

        repulse_nx, repulse_ny = 0.0, 0.0
        ball_radius = getattr(self.ball, "radius", 10.0)

        for entity in all_entities:
            if entity == target or entity == self.ball:
                continue

            entity_radius = getattr(entity, "radius", 10.0)
            dx = self.ball.x - entity.x
            dy = self.ball.y - entity.y
            dist_sq = dx*dx + dy*dy

            safe_dist = ball_radius + entity_radius + 5.0
            if dist_sq > 0.0001 and dist_sq < safe_dist * safe_dist:
                dist = math.sqrt(dist_sq)
                force = 1.0 - (dist / safe_dist)
                repulse_nx += (dx / dist) * force
                repulse_ny += (dy / dist) * force

        comb_nx = nx + repulse_nx * 0.5
        comb_ny = ny + repulse_ny * 0.5

        comb_dist_sq = comb_nx*comb_nx + comb_ny*comb_ny
        if comb_dist_sq > 0.0001:
            comb_dist = math.sqrt(comb_dist_sq)
            return comb_nx / comb_dist, comb_ny / comb_dist
        return nx, ny

    def _get_enemies(self) -> list:
        perception_radius = getattr(self.ball, "perception_radius", 250)
        if hasattr(self.world, "get_nearby_entities"):
            entities = self.world.get_nearby_entities(self.ball, perception_radius)
            if isinstance(entities, dict):
                return entities.get("enemies", [])
            else:
                return [e for e in entities if getattr(e, "ball_type", None) != self.ball.ball_type and getattr(e, "alive", True)]
        return []

    def _get_allies(self) -> list:
        perception_radius = getattr(self.ball, "perception_radius", 250)
        if hasattr(self.world, "get_nearby_entities"):
            entities = self.world.get_nearby_entities(self.ball, perception_radius)
            if isinstance(entities, dict):
                return entities.get("allies", [])
            else:
                return [e for e in entities if getattr(e, "ball_type", None) == self.ball.ball_type and getattr(e, "alive", True) and e != self.ball]
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

        nearest = min(enemies, key=lambda e: (e.x - self.ball.x) ** 2 + (e.y - self.ball.y) ** 2)
        dx, dy = self.ball.x - nearest.x, self.ball.y - nearest.y
        dist_sq = dx * dx + dy * dy
        dist = math.sqrt(dist_sq) if dist_sq > 0.0001 else 0.01

        perception_radius = getattr(self.ball, "perception_radius", 250)
        if dist > perception_radius * 0.8:
            self._idle(delta)
            return

        if dist < 0.01:
            dist = 0.01

        flee_nx = dx / dist
        flee_ny = dy / dist

        # Pull towards allies
        allies = self._get_allies()
        ally_nx, ally_ny = 0.0, 0.0
        if allies:
            nearest_ally = min(allies, key=lambda a: (a.x - self.ball.x) ** 2 + (a.y - self.ball.y) ** 2)
            adx, ady = nearest_ally.x - self.ball.x, nearest_ally.y - self.ball.y
            adist_sq = adx * adx + ady * ady
            if adist_sq > 0.0001:
                adist = math.sqrt(adist_sq)
                ally_nx = adx / adist
                ally_ny = ady / adist

        # Pull towards center (safe zone) if near edges
        safe_nx, safe_ny = 0.0, 0.0
        if hasattr(self.world, "width") and hasattr(self.world, "height"):
            center_x = self.world.width / 2
            center_y = self.world.height / 2
            cdx, cdy = center_x - self.ball.x, center_y - self.ball.y
            cdist_sq = cdx * cdx + cdy * cdy

            if cdist_sq > 0.0001:
                cdist = math.sqrt(cdist_sq)
                # Start pulling strongly if we are more than 30% away from the center
                if cdist > min(center_x, center_y) * 0.3:
                    safe_nx = cdx / cdist
                    safe_ny = cdy / cdist

        # Combine vectors
        # Heavily prioritize fleeing from threat, with moderate pull towards allies and safe zone
        comb_nx = flee_nx * 1.0 + ally_nx * 0.4 + safe_nx * 0.3
        comb_ny = flee_ny * 1.0 + ally_ny * 0.4 + safe_ny * 0.3

        comb_dist_sq = comb_nx * comb_nx + comb_ny * comb_ny
        if comb_dist_sq > 0.0001:
            comb_dist = math.sqrt(comb_dist_sq)
            comb_nx /= comb_dist
            comb_ny /= comb_dist
        else:
            comb_nx, comb_ny = flee_nx, flee_ny

        base_speed = getattr(self.ball, "speed", 2.0)
        boosted_speed = base_speed * 1.5

        self.ball.x += comb_nx * boosted_speed * delta * 60
        self.ball.y += comb_ny * boosted_speed * delta * 60

    def _attack(self, delta: float) -> None:
        enemies = self._get_enemies()
        if enemies:
            target = min(enemies, key=lambda e: (e.x - self.ball.x) ** 2 + (e.y - self.ball.y) ** 2)

            personality = getattr(self.ball, "personality", "idle")
            if personality == "sniper" and getattr(self.ball, "team_message", None) is None:
                self.ball.team_message = {"type": "target_spotted", "x": target.x, "y": target.y}

            dx, dy = target.x - self.ball.x, target.y - self.ball.y
            dist_sq = dx * dx + dy * dy
            if dist_sq > 0.0001:
                dist = math.sqrt(dist_sq)
                nx, ny = dx / dist, dy / dist
                nx, ny = self._apply_obstacle_avoidance(nx, ny, target)

                step = getattr(self.ball, "speed", 2.0) * delta * 60
                self.ball.x += nx * min(step, dist)
                self.ball.y += ny * min(step, dist)

            # Recalculate distance after movement
            dx, dy = target.x - self.ball.x, target.y - self.ball.y
            dist_sq = dx * dx + dy * dy
            dist = math.sqrt(dist_sq) if dist_sq > 0.0001 else 0.0

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
            dist_sq = dx * dx + dy * dy
            if dist_sq > 0.0001:
                dist = math.sqrt(dist_sq)
                nx, ny = dx / dist, dy / dist
                nx, ny = self._apply_obstacle_avoidance(nx, ny, nearest)

                step = getattr(self.ball, "speed", 2.0) * delta * 60
                self.ball.x += nx * min(step, dist)
                self.ball.y += ny * min(step, dist)

            # Recalculate distance after movement
            dx, dy = nearest.x - self.ball.x, nearest.y - self.ball.y
            dist_sq = dx * dx + dy * dy
            dist = math.sqrt(dist_sq) if dist_sq > 0.0001 else 0.0

            ball_radius = getattr(self.ball, "radius", 10.0)
            if dist <= ball_radius + 10:
                if hasattr(self.world, "_collect_booster"):
                    self.world._collect_booster(self.ball, nearest)
        else:
            self._idle(delta)

    def _use_skill(self) -> None:
        skill_timer = getattr(self.ball, "skill_timer", 0.0)
        if skill_timer <= 0 and hasattr(self.ball, "use_skill"):
            self.ball.use_skill()
            if hasattr(self.ball, "skill_cooldown"):
                self.ball.skill_timer = self.ball.skill_cooldown

    def _idle(self, delta: float) -> None:
        speed = getattr(self.ball, "speed", 2.0)
        self.ball.x += random.uniform(-1, 1) * speed * 0.3
        self.ball.y += random.uniform(-1, 1) * speed * 0.3

    def _clamp_position(self) -> None:
        radius = getattr(self.ball, "radius", 10.0)

        if math.isnan(self.ball.x) or math.isinf(self.ball.x):
            self.ball.x = getattr(self.world, "width", 1000) / 2
        if math.isnan(self.ball.y) or math.isinf(self.ball.y):
            self.ball.y = getattr(self.world, "height", 1000) / 2

        if hasattr(self.world, "width") and hasattr(self.world, "height"):
            self.ball.x = max(radius, min(self.world.width - radius, self.ball.x))
            self.ball.y = max(radius, min(self.world.height - radius, self.ball.y))

    def _update_skill_timer(self, delta: float) -> None:
        if hasattr(self.ball, "skill_timer") and self.ball.skill_timer > 0:
            self.ball.skill_timer -= delta
