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
        self._emit_team_messages(strategy)

    def _emit_team_messages(self, strategy: str) -> None:
        """
        Emits information to allies depending on ball state and personality.
        """
        message = None
        target_id = None

        hp_percent = 1.0
        if hasattr(self.ball, "get_hp_percent"):
            hp_percent = self.ball.get_hp_percent()
        elif hasattr(self.ball, "hp") and hasattr(self.ball, "max_hp"):
            hp_percent = float(self.ball.hp) / float(self.ball.max_hp)

        personality = getattr(self.ball, "personality", "idle")

        if hp_percent < 0.3:
            message = "help"
        elif strategy == "defend" and personality == "tank":
            message = "hold"
        elif personality == "healer" and strategy != "flee":
            message = "heal_call"
        elif strategy in ("attack", "chase"):
            enemies = self._get_enemies()
            if enemies:
                target = min(enemies, key=lambda e: (e.x - self.ball.x) ** 2 + (e.y - self.ball.y) ** 2)
                target_id = getattr(target, "id", None)
                if personality == "sniper":
                    message = "threat"
                else:
                    message = "target"

        if message:
            self.ball.team_message = {"type": message, "target_id": target_id}
        else:
            if hasattr(self.ball, "team_message"):
                self.ball.team_message = None

    def _get_allies(self) -> list:
        perception_radius = getattr(self.ball, "perception_radius", 250)
        if hasattr(self.world, "get_nearby_entities"):
            entities = self.world.get_nearby_entities(self.ball, perception_radius)
            if isinstance(entities, dict):
                return entities.get("allies", [])
            else:
                return [e for e in entities if getattr(e, "ball_type", None) == self.ball.ball_type and getattr(e, "alive", True)]
        return []

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

    def _flee(self, delta: float) -> None:
        enemies = self._get_enemies()
        if enemies:
            nearest = min(enemies, key=lambda e: (e.x - self.ball.x) ** 2 + (e.y - self.ball.y) ** 2)
            dx, dy = self.ball.x - nearest.x, self.ball.y - nearest.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 0.01:
                self.ball.x += (dx / dist) * getattr(self.ball, "speed", 2.0) * delta * 60
                self.ball.y += (dy / dist) * getattr(self.ball, "speed", 2.0) * delta * 60
        else:
            self._idle(delta)

    def _attack(self, delta: float) -> None:
        enemies = self._get_enemies()
        if enemies:
            # Check for called out targets from allies
            allies = self._get_allies()
            priority_target_id = None
            for ally in allies:
                msg = getattr(ally, "team_message", None)
                if msg and isinstance(msg, dict) and msg.get("type") in ("target", "threat"):
                    priority_target_id = msg.get("target_id")
                    if priority_target_id is not None:
                        break

            target = None
            if priority_target_id is not None:
                for e in enemies:
                    if getattr(e, "id", None) == priority_target_id:
                        target = e
                        break

            if not target:
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
        # Defend: move towards allies needing help, a holding tank, or a healer calling for wounded
        allies = self._get_allies()
        target_ally = None
        for ally in allies:
            msg = getattr(ally, "team_message", None)
            if msg and isinstance(msg, dict):
                msg_type = msg.get("type")
                if msg_type in ("help", "hold", "heal_call"):
                    target_ally = ally
                    break

        if target_ally:
            dx, dy = target_ally.x - self.ball.x, target_ally.y - self.ball.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 30.0:  # Don't overlap completely
                nx, ny = dx / dist, dy / dist
                step = getattr(self.ball, "speed", 2.0) * delta * 60
                self.ball.x += nx * min(step, dist)
                self.ball.y += ny * min(step, dist)
            else:
                self._idle(delta * 0.2)
        else:
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
