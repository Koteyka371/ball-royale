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

        old_x, old_y = self.ball.x, self.ball.y

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

        # Track movement for facing direction
        if delta > 0:
            dx = self.ball.x - old_x
            dy = self.ball.y - old_y
            dist = math.sqrt(dx*dx + dy*dy)
            if dist > 0.01:
                self.ball.facing_x = dx / dist
                self.ball.facing_y = dy / dist
            elif not hasattr(self.ball, "facing_x"):
                self.ball.facing_x = 0.0
                self.ball.facing_y = 1.0

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
        dist = math.sqrt(dx * dx + dy * dy)

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
            adist = math.sqrt(adx * adx + ady * ady)
            if adist > 0.01:
                ally_nx = adx / adist
                ally_ny = ady / adist

        # Pull towards center (safe zone) if near edges
        safe_nx, safe_ny = 0.0, 0.0
        if hasattr(self.world, "width") and hasattr(self.world, "height"):
            center_x = self.world.width / 2
            center_y = self.world.height / 2
            cdx, cdy = center_x - self.ball.x, center_y - self.ball.y
            cdist = math.sqrt(cdx * cdx + cdy * cdy)

            # Start pulling strongly if we are more than 30% away from the center
            if cdist > min(center_x, center_y) * 0.3 and cdist > 0.01:
                safe_nx = cdx / cdist
                safe_ny = cdy / cdist

        # Combine vectors
        # Heavily prioritize fleeing from threat, with moderate pull towards allies and safe zone
        comb_nx = flee_nx * 1.0 + ally_nx * 0.4 + safe_nx * 0.3
        comb_ny = flee_ny * 1.0 + ally_ny * 0.4 + safe_ny * 0.3

        comb_dist = math.sqrt(comb_nx * comb_nx + comb_ny * comb_ny)
        if comb_dist > 0.01:
            comb_nx /= comb_dist
            comb_ny /= comb_dist

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

            target_facing_x = getattr(target, "facing_x", 0.0)
            target_facing_y = getattr(target, "facing_y", 1.0)

            dx, dy = target.x - self.ball.x, target.y - self.ball.y
            dist = math.sqrt(dx * dx + dy * dy)
            target_radius = getattr(target, "radius", 10.0)
            ball_radius = getattr(self.ball, "radius", 10.0)

            is_flanking = False
            behind_target = False

            if dist > 0.01:
                nx, ny = dx / dist, dy / dist

                # Check if we are behind the target (dot product > 0.5 roughly)
                dot_prod = nx * target_facing_x + ny * target_facing_y
                behind_target = dot_prod > 0.5

                step = getattr(self.ball, "speed", 2.0) * delta * 60

                if personality in ("ninja", "scout") and not behind_target and dist > ball_radius + target_radius + 15:
                    is_flanking = True
                    # Steer towards a point behind the target
                    behind_x = target.x - target_facing_x * (target_radius + ball_radius + 20)
                    behind_y = target.y - target_facing_y * (target_radius + ball_radius + 20)
                    bdx, bdy = behind_x - self.ball.x, behind_y - self.ball.y
                    bdist = math.sqrt(bdx*bdx + bdy*bdy)
                    if bdist > 0.01:
                        nx, ny = bdx / bdist, bdy / bdist
                        step *= 1.5 # Move faster while flanking

                self.ball.x += nx * min(step, dist if not is_flanking else bdist)
                self.ball.y += ny * min(step, dist if not is_flanking else bdist)

            # Recalculate distance after moving to see if we can hit
            dx, dy = target.x - self.ball.x, target.y - self.ball.y
            dist = math.sqrt(dx * dx + dy * dy)

            if dist <= ball_radius + target_radius + 5:
                if hasattr(self.world, "_deal_damage"):
                    original_damage = getattr(self.ball, "damage", 0)
                    # Recalculate behind_target at hit time
                    if dist > 0.01:
                        nx, ny = dx / dist, dy / dist
                        dot_prod = nx * target_facing_x + ny * target_facing_y
                        behind_target = dot_prod > 0.5

                    if behind_target and personality in ("ninja", "scout"):
                        self.ball.damage = original_damage * 2.0

                    self.world._deal_damage(self.ball, target)

                    if behind_target and personality in ("ninja", "scout"):
                        self.ball.damage = original_damage
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
