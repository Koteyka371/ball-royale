import math
from typing import Any
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
        old_x = getattr(self.ball, "x", 0.0)
        old_y = getattr(self.ball, "y", 0.0)

        # Update shrinking zone and apply damage
        if hasattr(self.world, "arena") and hasattr(self.world.arena, "update_zone"):
            current_tick = getattr(self.world, "tick", 0)
            self.world.arena.update_zone(current_tick, delta)

            ball_type = getattr(self.ball, "ball_type", None)
            if ball_type != "spectator":
                cx, cy = getattr(self.world.arena, "safe_zone_center", (0, 0))
                radius = getattr(self.world.arena, "safe_zone_radius", float('inf'))
                dist = math.sqrt((self.ball.x - cx)**2 + (self.ball.y - cy)**2)
                if dist > radius:
                    zone_damage = 10.0 * delta
                    if hasattr(self.ball, "take_damage"):
                        self.ball.take_damage(zone_damage)
                    elif hasattr(self.ball, "hp"):
                        self.ball.hp -= zone_damage
                        if self.ball.hp <= 0:
                            self.ball.alive = False

            # Apply hazard damage
            if hasattr(self.world.arena, "hazards") and ball_type != "spectator":
                for hazard in self.world.arena.hazards:
                    dist = math.sqrt((self.ball.x - hazard.x)**2 + (self.ball.y - hazard.y)**2)
                    if dist < (self.ball.radius + hazard.radius):
                        hazard_damage = hazard.damage * delta
                        if hasattr(self.ball, "take_damage"):
                            self.ball.take_damage(hazard_damage)
                        elif hasattr(self.ball, "hp"):
                            self.ball.hp -= hazard_damage
                            if self.ball.hp <= 0:
                                self.ball.alive = False

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
        elif strategy == "attack":
            self._attack(delta)
        elif strategy == "kite":
            self._kite(delta)
        elif strategy == "chase":
            self._chase(delta)
        elif strategy == "flank":
            self._flank(delta)
        elif strategy == "group_attack":
            self._group_attack(delta)
        elif strategy == "defend":
            self._defend(delta)
        elif strategy in ("opportunistic", "collect_booster", "collect booster"):
            self._collect_booster(delta)
        elif strategy in ("use_skill", "use skill", "action_skill", "Действие"):
            if getattr(self.ball, "skill", "") == "flank":
                self.ball.current_action = "flank"
                self._flank(delta)
            else:
                self._use_skill()
        else:
            self._idle(delta)

        bounced_col = self._resolve_collisions()
        bounced_wall = self._clamp_position()
        if bounced_wall or bounced_col:
            self._trigger_ripple_effect()

        self._update_skill_timer(delta)

        if delta > 0:
            self.ball.vx = (self.ball.x - old_x) / delta
            self.ball.vy = (self.ball.y - old_y) / delta



    def _apply_boid_rules(self, nx: float, ny: float) -> tuple[float, float]:
        b_type = getattr(self.ball, "ball_type", "")
        if b_type != "swarm":
            return nx, ny

        allies = self._get_allies()
        if not allies:
            return nx, ny

        cohesion_weight = 0.5
        alignment_weight = 0.5
        separation_weight = 1.0

        center_x, center_y = 0.0, 0.0
        align_vx, align_vy = 0.0, 0.0
        sep_nx, sep_ny = 0.0, 0.0

        count = 0
        perception_radius = getattr(self.ball, "perception_radius", 250)

        for ally in allies:
            dx = self.ball.x - ally.x
            dy = self.ball.y - ally.y
            dist_sq = dx*dx + dy*dy

            if 0.0001 < dist_sq < perception_radius * perception_radius:
                count += 1
                dist = math.sqrt(dist_sq)

                center_x += ally.x
                center_y += ally.y

                align_vx += getattr(ally, "vx", 0.0)
                align_vy += getattr(ally, "vy", 0.0)

                sep_dist = (getattr(self.ball, "radius", 10.0) + getattr(ally, "radius", 10.0)) * 2.0
                if dist < sep_dist:
                    sep_nx += (dx / dist) / dist
                    sep_ny += (dy / dist) / dist

        if count > 0:
            center_x /= count
            center_y /= count

            coh_dx = center_x - self.ball.x
            coh_dy = center_y - self.ball.y
            coh_dist_sq = coh_dx*coh_dx + coh_dy*coh_dy
            if coh_dist_sq > 0.0001:
                coh_dist = math.sqrt(coh_dist_sq)
                coh_nx = coh_dx / coh_dist
                coh_ny = coh_dy / coh_dist
            else:
                coh_nx, coh_ny = 0.0, 0.0

            align_vx /= count
            align_vy /= count
            align_speed_sq = align_vx*align_vx + align_vy*align_vy
            if align_speed_sq > 0.0001:
                align_speed = math.sqrt(align_speed_sq)
                al_nx = align_vx / align_speed
                al_ny = align_vy / align_speed
            else:
                al_nx, al_ny = 0.0, 0.0

            comb_nx = nx + coh_nx * cohesion_weight + al_nx * alignment_weight + sep_nx * separation_weight
            comb_ny = ny + coh_ny * cohesion_weight + al_ny * alignment_weight + sep_ny * separation_weight

            comb_dist_sq = comb_nx*comb_nx + comb_ny*comb_ny
            if comb_dist_sq > 0.0001:
                comb_dist = math.sqrt(comb_dist_sq)
                return comb_nx / comb_dist, comb_ny / comb_dist

        return nx, ny

    def _apply_obstacle_avoidance(self, nx: float, ny: float, target: Any = None, ignore_enemies: bool = False) -> tuple[float, float]:
        """Applies a repulsive force from nearby entities to avoid collisions."""
        all_entities = []
        perception_radius = getattr(self.ball, "perception_radius", 250)

        if hasattr(self.world, "get_nearby_entities"):
            entities = self.world.get_nearby_entities(self.ball, perception_radius)
            if isinstance(entities, dict):
                for key in ["enemies", "allies"]:
                    if ignore_enemies and key == "enemies":
                        continue
                    all_entities.extend(entities.get(key, []))
            else:
                all_entities = [e for e in entities if getattr(e, "alive", True) and e != self.ball]
                if ignore_enemies:
                    # Filter out enemies, but keep allies, boosters, and neutral obstacles.
                    # An enemy is defined as having a ball_type that isn't the ball's type,
                    # AND it is not a 'booster' or similar neutral item.
                    # Simplest heuristic here: if we are supposed to ignore enemies,
                    # only ignore those whose ball_type is different AND not a known neutral/booster.
                    filtered = []
                    for e in all_entities:
                        b_type = getattr(e, "ball_type", None)
                        is_enemy = (b_type is not None and b_type != self.ball.ball_type and b_type != "booster")
                        if not is_enemy:
                            filtered.append(e)
                    all_entities = filtered

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
                return [e for e in entities.get("enemies", []) if getattr(e, "ball_type", None) != "spectator"]
            else:
                return [e for e in entities if getattr(e, "ball_type", None) != self.ball.ball_type and getattr(e, "ball_type", None) != "spectator" and getattr(e, "alive", True)]
        return []

    def _get_allies(self) -> list:
        perception_radius = getattr(self.ball, "perception_radius", 250)
        if hasattr(self.world, "get_nearby_entities"):
            entities = self.world.get_nearby_entities(self.ball, perception_radius)
            if isinstance(entities, dict):
                return [e for e in entities.get("allies", []) if getattr(e, "ball_type", None) != "spectator"]
            else:
                return [e for e in entities if getattr(e, "ball_type", None) == self.ball.ball_type and getattr(e, "ball_type", None) != "spectator" and getattr(e, "alive", True) and e != self.ball]
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

        comb_nx, comb_ny = self._apply_boid_rules(comb_nx, comb_ny)

        base_speed = getattr(self.ball, "speed", 2.0)
        boosted_speed = base_speed * 1.5

        emotion = getattr(self.ball, "emotion", "neutral")
        if emotion == "fear":
            boosted_speed *= 1.5

        self.ball.x += comb_nx * boosted_speed * delta * 60
        self.ball.y += comb_ny * boosted_speed * delta * 60

    def _get_strongest_enemy(self, enemies: list[Any]) -> Any:
        return max(enemies, key=lambda e: (
            getattr(e, "max_hp", getattr(e, "hp", 0.0)),
            getattr(e, "hp", 0.0),
            -((e.x - self.ball.x)**2 + (e.y - self.ball.y)**2),
            getattr(e, "id", 0)
        ))

    def _get_target(self, enemies: list[Any]) -> Any:
        # Check for rivals first
        my_memory = getattr(self.ball, "memory", {})
        # Extract all rivals from memory
        rivals = []
        for e in enemies:
            if hasattr(e, "id"):
                rel_data = my_memory.get(e.id, {})
                if rel_data.get("relation") == "rival":
                    rivals.append(e)
        if rivals:
            return min(rivals, key=lambda e: (e.x - self.ball.x) ** 2 + (e.y - self.ball.y) ** 2)

        target_msg = None
        allies = self._get_allies()
        for ally in allies:
            msg = getattr(ally, "team_message", None)
            if msg and isinstance(msg, dict) and msg.get("type") == "target_spotted":
                target_msg = msg
                break

        if target_msg:
            tx, ty = target_msg.get("x", self.ball.x), target_msg.get("y", self.ball.y)
            return min(enemies, key=lambda e: (e.x - tx) ** 2 + (e.y - ty) ** 2)
        else:
            b_type = getattr(self.ball, "ball_type", getattr(self.ball.__class__, "BALL_TYPE", "")).lower()
            if b_type == "tank":
                return self._get_strongest_enemy(enemies)
            elif b_type == "bomber":
                def count_nearby(e1):
                    return sum(1 for e2 in enemies if e1 != e2 and ((e1.x - e2.x)**2 + (e1.y - e2.y)**2) <= 1600)
                return max(enemies, key=lambda e: (count_nearby(e), -((self.ball.x - e.x)**2 + (self.ball.y - e.y)**2)))
            else:
                return min(enemies, key=lambda e: (e.x - self.ball.x) ** 2 + (e.y - self.ball.y) ** 2)


    def _group_attack(self, delta: float) -> None:
        enemies = self._get_enemies()
        allies = self._get_allies()

        if enemies:
            target = self._get_target(enemies)

            personality = getattr(self.ball, "personality", "idle")
            if personality in ("warrior", "sniper", "assassin", "berserker", "bomber", "phantom", "rogue", "swarm", "aggressive", "cunning", "curious", "mage", "paladin", "necro", "druid", "bard", "monk", "warlock", "cleric", "ranger", "illusionist", "alchemist", "shaman", "jester") and getattr(self.ball, "team_message", None) is None:
                self.ball.team_message = {"type": "target_spotted", "x": target.x, "y": target.y}

            dx, dy = target.x - self.ball.x, target.y - self.ball.y
            dist_sq = dx * dx + dy * dy
            if dist_sq > 0.0001:
                import math
                dist = math.sqrt(dist_sq)
                nx, ny = dx / dist, dy / dist

                # Apply boid-like cohesion to stick with allies
                cohesion_x, cohesion_y = 0.0, 0.0
                if allies:
                    for ally in allies:
                        cohesion_x += ally.x
                        cohesion_y += ally.y
                    cohesion_x /= len(allies)
                    cohesion_y /= len(allies)

                    cdx, cdy = cohesion_x - self.ball.x, cohesion_y - self.ball.y
                    cdist_sq = cdx * cdx + cdy * cdy
                    if cdist_sq > 0.0001:
                        cdist = math.sqrt(cdist_sq)
                        cnx, cny = cdx / cdist, cdy / cdist

                        # Blend movement: 60% towards target, 40% towards allies center
                        nx = nx * 0.6 + cnx * 0.4
                        ny = ny * 0.6 + cny * 0.4

                        ndist_sq = nx * nx + ny * ny
                        if ndist_sq > 0.0001:
                            ndist = math.sqrt(ndist_sq)
                            nx /= ndist
                            ny /= ndist

                target_radius = getattr(target, "radius", 10.0)
                ball_radius = getattr(self.ball, "radius", 10.0)
                attack_range = ball_radius + target_radius + 5

                if nx != 0.0 or ny != 0.0:
                    nx, ny = self._apply_obstacle_avoidance(nx, ny, target)
                    nx, ny = self._apply_boid_rules(nx, ny)

                    step = getattr(self.ball, "speed", 2.0) * delta * 60
                    self.ball.x += nx * min(step, dist)
                    self.ball.y += ny * min(step, dist)

            # Recalculate distance
            dx, dy = target.x - self.ball.x, target.y - self.ball.y
            dist_sq = dx * dx + dy * dy
            dist = math.sqrt(dist_sq) if dist_sq > 0.0001 else 0.0

            target_radius = getattr(target, "radius", 10.0)
            ball_radius = getattr(self.ball, "radius", 10.0)
            attack_range = ball_radius + target_radius + 5

            skill_timer = getattr(self.ball, "skill_timer", 0.0)
            if skill_timer <= 0 and dist <= attack_range * 1.5:
                if hasattr(self.ball, "use_skill"):
                    self.ball.use_skill()
                self.ball.skill_timer = getattr(self.ball, "skill_cooldown", 5.0)

            attack_timer = getattr(self.ball, "attack_timer", 0.0)
            if attack_timer <= 0 and dist <= attack_range:
                if hasattr(self.world, "_deal_damage"):
                    self.world._deal_damage(self.ball, target)
                    if hasattr(target, "id") and hasattr(self.ball, "id"):
                        # Rivalry memory update
                        if not hasattr(target, "memory"):
                            target.memory = {}
                        target.memory[self.ball.id] = {"relation": "rival"}
                speed = getattr(self.ball, "speed", 2.0)
                cooldown = max(0.2, 2.0 / speed if speed > 0 else 1.0)
                self.ball.attack_timer = cooldown
        else:
            self._idle(delta)


    def _get_flank_target(self, enemies: list) -> Any:
        best_target = None
        best_score = (-float('inf'), -float('inf'), -float('inf'))

        for e in enemies:
            dx = e.x - self.ball.x
            dy = e.y - self.ball.y
            dist_sq = dx * dx + dy * dy
            dist = math.sqrt(dist_sq) if dist_sq > 0 else 0.0

            target_vx = getattr(e, "vx", 0.0)
            target_vy = getattr(e, "vy", 0.0)

            if abs(target_vx) < 0.1 and abs(target_vy) < 0.1:
                target_vx = getattr(e, 'last_vx', 1.0)
                target_vy = getattr(e, 'last_vy', 0.0)
                if abs(target_vx) < 0.1 and abs(target_vy) < 0.1:
                    target_vx, target_vy = 1.0, 0.0
            else:
                v_dist_sq = target_vx * target_vx + target_vy * target_vy
                if v_dist_sq > 0.0001:
                    v_dist = math.sqrt(v_dist_sq)
                    target_vx /= v_dist
                    target_vy /= v_dist

            # Are they moving away from us?
            # We want dot_product > 0 (they face away)
            dot_product = 0.0
            if dist > 0.0001:
                dot_product = (dx / dist) * target_vx + (dy / dist) * target_vy

            # Tiebreaker score: (is_facing_away, -distance, id)
            # We want to flank targets whose back is turned towards us.
            score = (dot_product, -dist, getattr(e, 'id', 0))
            if best_target is None or score > best_score:
                best_score = score
                best_target = e

        return best_target

    def _get_flank_position(self, target: Any) -> tuple[float, float, float, float]:
        target_vx = getattr(target, "vx", 0.0)
        target_vy = getattr(target, "vy", 0.0)

        if abs(target_vx) < 0.1 and abs(target_vy) < 0.1:
            target_vx = getattr(target, 'last_vx', 1.0)
            target_vy = getattr(target, 'last_vy', 0.0)
            if abs(target_vx) < 0.1 and abs(target_vy) < 0.1:
                target_vx, target_vy = 1.0, 0.0
        else:
            v_dist_sq = target_vx * target_vx + target_vy * target_vy
            if v_dist_sq > 0.0001:
                v_dist = math.sqrt(v_dist_sq)
                target_vx /= v_dist
                target_vy /= v_dist

        flank_distance = getattr(target, 'radius', 10.0) * 2.0 + 20.0
        flank_x = target.x - target_vx * flank_distance
        flank_y = target.y - target_vy * flank_distance

        return target_vx, target_vy, flank_x, flank_y
    def _flank(self, delta: float) -> None:
        enemies = self._get_enemies()
        if enemies:
            target = self._get_flank_target(enemies)

            # Announce target
            personality = getattr(self.ball, "personality", "idle")
            if personality in ("warrior", "sniper", "assassin", "berserker", "bomber", "phantom", "rogue", "swarm", "aggressive", "cunning", "curious", "mage", "paladin", "necro", "druid", "bard", "monk", "warlock", "cleric", "ranger", "illusionist", "alchemist", "shaman", "jester") and getattr(self.ball, "team_message", None) is None:
                self.ball.team_message = {"type": "target_spotted", "x": target.x, "y": target.y}

            target_vx, target_vy, flank_x, flank_y = self._get_flank_position(target)

            dx, dy = flank_x - self.ball.x, flank_y - self.ball.y
            dist_sq = dx * dx + dy * dy
            if dist_sq > 0.0001:
                dist = math.sqrt(dist_sq)
                nx, ny = dx / dist, dy / dist

                if nx != 0.0 or ny != 0.0:
                    nx, ny = self._apply_obstacle_avoidance(nx, ny, target)
                    nx, ny = self._apply_boid_rules(nx, ny)

                    step = getattr(self.ball, "speed", 2.0) * delta * 60
                    self.ball.x += nx * min(step, dist)
                    self.ball.y += ny * min(step, dist)

            # Calculate direct distance to target for attack
            direct_dx, direct_dy = target.x - self.ball.x, target.y - self.ball.y
            direct_dist_sq = direct_dx * direct_dx + direct_dy * direct_dy
            direct_dist = math.sqrt(direct_dist_sq) if direct_dist_sq > 0.0001 else 0.0

            target_radius = getattr(target, "radius", 10.0)
            ball_radius = getattr(self.ball, "radius", 10.0)
            attack_range = ball_radius + target_radius + 5

            # Use skill if available and we are somewhat far from the actual target (gap closing)
            skill_timer = getattr(self.ball, "skill_timer", 0.0)
            if skill_timer <= 0 and direct_dist > attack_range * 1.5:
                if hasattr(self.ball, "use_skill"):
                    self.ball.use_skill()
                if hasattr(self.ball, "skill_cooldown"):
                    self.ball.skill_timer = self.ball.skill_cooldown

            if direct_dist <= attack_range:
                attack_timer = getattr(self.ball, "attack_timer", 0.0)
                if attack_timer <= 0:
                    # Check if attacking from behind (dot product of target velocity and attack direction)
                    # We are behind if the target is moving AWAY from us
                    # direction to target = direct_dx/direct_dist, direct_dy/direct_dist
                    dot_product = 0.0
                    if direct_dist > 0.0001:
                        ndx, ndy = direct_dx / direct_dist, direct_dy / direct_dist
                        dot_product = ndx * target_vx + ndy * target_vy

                    is_critical = dot_product > 0.5

                    # Temporarily boost damage if critical
                    original_damage = getattr(self.ball, "damage", 5.0)
                    if is_critical:
                        if getattr(self.ball, 'ball_type', '') == 'ninja':
                            self.ball.damage = original_damage * 3.0
                        else:
                            self.ball.damage = original_damage * 2.0

                    if hasattr(self.world, "_deal_damage"):
                        self.world._deal_damage(self.ball, target)
                        if hasattr(target, "id") and hasattr(self.ball, "id"):
                            # Rivalry memory update
                            if not hasattr(target, "memory"):
                                target.memory = {}
                            target.memory[self.ball.id] = {"relation": "rival"}

                    # Restore damage
                    if is_critical:
                        self.ball.damage = original_damage

                    speed = getattr(self.ball, "speed", 2.0)
                    cooldown = max(0.2, 2.0 / speed if speed > 0 else 1.0)
                    self.ball.attack_timer = cooldown
        else:
            self._idle(delta)

    def _chase(self, delta: float) -> None:
        enemies = self._get_enemies()
        if not enemies:
            self._idle(delta)
            return

        target = self._get_target(enemies)

        personality = getattr(self.ball, "personality", "idle")
        if personality in ("warrior", "sniper", "assassin", "berserker", "bomber", "phantom", "rogue", "swarm", "aggressive", "cunning", "curious", "mage", "paladin", "necro", "druid", "bard", "monk", "warlock", "cleric", "ranger", "illusionist", "alchemist", "shaman", "jester") and getattr(self.ball, "team_message", None) is None:
            self.ball.team_message = {"type": "target_spotted", "x": target.x, "y": target.y}

        # Basic pathfinding / steering:
        # Move towards target, but be repelled by obstacles (other entities)
        target_dx = target.x - self.ball.x
        target_dy = target.y - self.ball.y
        dist_to_target = math.sqrt(target_dx * target_dx + target_dy * target_dy)

        target_radius = getattr(target, "radius", 10.0)
        ball_radius = getattr(self.ball, "radius", 10.0)
        b_type_chase = getattr(self.ball, "ball_type", getattr(self.ball.__class__, "BALL_TYPE", "")).lower()
        if b_type_chase == "sniper":
            attack_range = 150.0
        else:
            attack_range = ball_radius + target_radius + 5

        # Stop moving if in attack range
        nx, ny = 0.0, 0.0
        if dist_to_target <= attack_range:
            if b_type_chase == "sniper" and dist_to_target < attack_range * 0.8:
                if dist_to_target > 0.01:
                    nx = -target_dx / dist_to_target
                    ny = -target_dy / dist_to_target
            else:
                # We are close enough, attack. No cooldown checking here, we just stop moving towards the target and wait for attack logic.
                # However we need to actually deal damage based on cooldowns, or just rely on the _attack strategy to do it.
                # Since this is _chase, it is just for movement, but it used to call _deal_damage directly.
                if hasattr(self.world, "_deal_damage"):
                    attack_timer = getattr(self.ball, "attack_timer", 0.0)
                    if attack_timer <= 0:
                        self.world._deal_damage(self.ball, target)
                        if hasattr(target, "id") and hasattr(self.ball, "id"):
                            # Rivalry memory update
                            if not hasattr(target, "memory"):
                                target.memory = {}
                            target.memory[self.ball.id] = {"relation": "rival"}
                        self.ball.attack_timer = max(0.2, 2.0 / getattr(self.ball, "speed", 2.0))
                return
        else:
            if dist_to_target > 0.01:
                if b_type_chase == "ninja":
                    tvx = getattr(target, "vx", 0.0)
                    tvy = getattr(target, "vy", 0.0)
                    tv_dist_sq = tvx*tvx + tvy*tvy
                    if tv_dist_sq > 0.0001:
                        tv_dist = math.sqrt(tv_dist_sq)
                        back_x = target.x - (tvx / tv_dist) * (target_radius + ball_radius + 5.0)
                        back_y = target.y - (tvy / tv_dist) * (target_radius + ball_radius + 5.0)
                        bdx = back_x - self.ball.x
                        bdy = back_y - self.ball.y
                        b_dist = math.sqrt(bdx*bdx + bdy*bdy)
                        if b_dist > 0.01:
                            nx = bdx / b_dist
                            ny = bdy / b_dist
                        else:
                            nx = target_dx / dist_to_target
                            ny = target_dy / dist_to_target
                    else:
                        nx = target_dx / dist_to_target
                        ny = target_dy / dist_to_target
                else:
                    nx = target_dx / dist_to_target
                    ny = target_dy / dist_to_target

        # Obstacle avoidance: repel from nearby allies and other enemies
        repel_x, repel_y = 0.0, 0.0
        all_entities = self._get_allies() + [e for e in enemies if e != target]
        for entity in all_entities:
            edx = self.ball.x - entity.x
            edy = self.ball.y - entity.y
            edist = math.sqrt(edx * edx + edy * edy)
            if edist > 0.01 and edist < (ball_radius + getattr(entity, "radius", 10.0)) * 2:
                # Repel force inversely proportional to distance
                repel_force = 1.0 / edist
                repel_x += (edx / edist) * repel_force
                repel_y += (edy / edist) * repel_force

        # Combine vectors
        comb_nx = nx + repel_x * 10.0
        comb_ny = ny + repel_y * 10.0
        comb_dist = math.sqrt(comb_nx * comb_nx + comb_ny * comb_ny)
        if comb_dist > 0.01:
            comb_nx /= comb_dist
            comb_ny /= comb_dist

        comb_nx, comb_ny = self._apply_boid_rules(comb_nx, comb_ny)

        step = getattr(self.ball, "speed", 2.0) * delta * 60
        self.ball.x += comb_nx * step
        self.ball.y += comb_ny * step

    def _attack(self, delta: float) -> None:
        enemies = self._get_enemies()
        if enemies:
            target = self._get_target(enemies)

            personality = getattr(self.ball, "personality", "idle")
            if personality in ("warrior", "sniper", "assassin", "berserker", "bomber", "phantom", "rogue", "swarm", "aggressive", "cunning", "curious", "mage", "paladin", "necro", "druid", "bard", "monk", "warlock", "cleric", "ranger", "illusionist", "alchemist", "shaman", "jester") and getattr(self.ball, "team_message", None) is None:
                self.ball.team_message = {"type": "target_spotted", "x": target.x, "y": target.y}

            dx, dy = target.x - self.ball.x, target.y - self.ball.y
            dist_sq = dx * dx + dy * dy
            if dist_sq > 0.0001:
                dist = math.sqrt(dist_sq)
                nx, ny = dx / dist, dy / dist

                target_radius = getattr(target, "radius", 10.0)
                ball_radius = getattr(self.ball, "radius", 10.0)

                attack_range = ball_radius + target_radius + 5

                if getattr(self.ball, "ball_type", getattr(self.ball.__class__, "BALL_TYPE", "")).lower() == "ninja":
                    tvx = getattr(target, "vx", 0.0)
                    tvy = getattr(target, "vy", 0.0)
                    tv_dist_sq = tvx*tvx + tvy*tvy
                    if tv_dist_sq > 0.0001:
                        tv_dist = math.sqrt(tv_dist_sq)
                        back_x = target.x - (tvx / tv_dist) * (target_radius + ball_radius + 5.0)
                        back_y = target.y - (tvy / tv_dist) * (target_radius + ball_radius + 5.0)
                        bdx = back_x - self.ball.x
                        bdy = back_y - self.ball.y
                        b_dist = math.sqrt(bdx*bdx + bdy*bdy)
                        if b_dist > 0.01:
                            nx = bdx / b_dist
                            ny = bdy / b_dist

                if nx != 0.0 or ny != 0.0:
                    nx, ny = self._apply_obstacle_avoidance(nx, ny, target)
                    nx, ny = self._apply_boid_rules(nx, ny)

                    step = getattr(self.ball, "speed", 2.0) * delta * 60
                    self.ball.x += nx * min(step, dist)
                    self.ball.y += ny * min(step, dist)

            # Recalculate distance after movement
            dx, dy = target.x - self.ball.x, target.y - self.ball.y
            dist_sq = dx * dx + dy * dy
            dist = math.sqrt(dist_sq) if dist_sq > 0.0001 else 0.0

            target_radius = getattr(target, "radius", 10.0)
            ball_radius = getattr(self.ball, "radius", 10.0)
            attack_range = ball_radius + target_radius + 5

            if dist <= attack_range:
                # Uses skill when available and optimal
                skill_timer = getattr(self.ball, "skill_timer", 0.0)
                if skill_timer <= 0:
                    optimal = True
                    b_type = getattr(self.ball, "ball_type", "")
                    if b_type == "bomber":
                        close_enemies = sum(1 for e in enemies if math.sqrt((e.x - self.ball.x)**2 + (e.y - self.ball.y)**2) <= ball_radius + getattr(e, "radius", 10.0) + 15)
                        optimal = close_enemies >= 3

                        # Suicide attack: guarantee explosion
                        if optimal:
                            self.ball.hp = 0 # Suicide
                            self.ball.alive = False
                    elif b_type == "tank":
                        optimal = (target == self._get_strongest_enemy(enemies))
                    elif b_type == "warrior":
                        in_front = 0
                        # Calculate normalized movement vector towards target
                        move_dx, move_dy = target.x - self.ball.x, target.y - self.ball.y
                        move_dist = math.sqrt(move_dx**2 + move_dy**2)
                        if move_dist > 0.0001:
                            mnx, mny = move_dx / move_dist, move_dy / move_dist
                            for e in enemies:
                                edx, edy = e.x - self.ball.x, e.y - self.ball.y
                                edist = math.sqrt(edx**2 + edy**2)
                                if edist <= ball_radius + getattr(e, "radius", 10.0) + 40 and edist > 0.0001:
                                    enx, eny = edx / edist, edy / edist
                                    dot_product = mnx * enx + mny * eny
                                    if dot_product > 0.5:
                                        in_front += 1
                        optimal = in_front >= 2

                    if optimal:
                        if hasattr(self.ball, "use_skill"):
                            self.ball.use_skill()
                        self.ball.skill_timer = getattr(self.ball, "skill_cooldown", 5.0)

                # Deal damage with attack timer
                attack_timer = getattr(self.ball, "attack_timer", 0.0)
                if attack_timer <= 0:
                    b_type = getattr(self.ball, "ball_type", "").lower()
                    original_damage = getattr(self.ball, "damage", 10.0)

                    if b_type == "ninja":
                        tvx = getattr(target, "vx", 0.0)
                        tvy = getattr(target, "vy", 0.0)
                        tv_dist_sq = tvx*tvx + tvy*tvy
                        if tv_dist_sq > 0.0001:
                            tv_dist = math.sqrt(tv_dist_sq)
                            tnx, tny = tvx/tv_dist, tvy/tv_dist

                            adx = target.x - self.ball.x
                            ady = target.y - self.ball.y
                            adist_sq = adx*adx + ady*ady
                            if adist_sq > 0.0001:
                                adist = math.sqrt(adist_sq)
                                anx, any = adx/adist, ady/adist

                                dot_product = anx * tnx + any * tny
                                if dot_product > 0.5:
                                    self.ball.damage = original_damage * 2.0

                    if hasattr(self.world, "_deal_damage"):
                        self.world._deal_damage(self.ball, target)
                        if hasattr(target, "id") and hasattr(self.ball, "id"):
                            # Rivalry memory update
                            if not hasattr(target, "memory"):
                                target.memory = {}
                            target.memory[self.ball.id] = {"relation": "rival"}

                    if b_type == "ninja":
                        self.ball.damage = original_damage

                    if b_type in ("scout", "assassin", "phantom", "swarm", "rogue", "ninja"):
                        cooldown = 0.3
                    elif b_type in ("tank", "juggernaut", "guardian"):
                        cooldown = 1.5
                    else:
                        speed = getattr(self.ball, "speed", 2.0)
                        cooldown = max(0.2, 2.0 / speed if speed > 0 else 1.0)
                    self.ball.attack_timer = cooldown
        else:
            self._idle(delta)

    def _defend(self, delta: float) -> None:
        personality = getattr(self.ball, "personality", "idle")
        if personality in ("tank", "defender", "guardian", "juggernaut"):
            enemies = self._get_enemies()
            if enemies:
                b_type = getattr(self.ball, "ball_type", getattr(self.ball.__class__, "BALL_TYPE", "")).lower()
                target_enemy = None
                target_pos_x = self.ball.x
                target_pos_y = self.ball.y
                should_move = False

                if b_type == "tank":
                    allies = self._get_allies()
                    ally_to_protect = None
                    if allies:
                        # Prioritize healers, then lowest HP
                        healers = [a for a in allies if getattr(a, "ball_type", getattr(a.__class__, "BALL_TYPE", "")).lower() == "healer"]
                        if healers:
                            ally_to_protect = min(healers, key=lambda a: (a.x - self.ball.x)**2 + (a.y - self.ball.y)**2)
                        else:
                            def get_hp_pct(a):
                                if hasattr(a, "get_hp_percent"):
                                    return a.get_hp_percent()
                                if hasattr(a, "hp") and hasattr(a, "max_hp"):
                                    return float(a.hp) / float(a.max_hp) if a.max_hp > 0 else 1.0
                                return 1.0
                            ally_to_protect = min(allies, key=lambda a: get_hp_pct(a))

                    target_enemy = self._get_strongest_enemy(enemies)

                    if ally_to_protect:
                        # Body blocking position: 30 units from ally towards enemy
                        ex, ey = target_enemy.x, target_enemy.y
                        ax, ay = ally_to_protect.x, ally_to_protect.y
                        dx_ea = ex - ax
                        dy_ea = ey - ay
                        dist_ea = math.sqrt(dx_ea*dx_ea + dy_ea*dy_ea)
                        if dist_ea > 0.0001:
                            target_pos_x = ax + (dx_ea / dist_ea) * min(30.0, dist_ea * 0.5)
                            target_pos_y = ay + (dy_ea / dist_ea) * min(30.0, dist_ea * 0.5)
                            should_move = True
                    else:
                        target_pos_x = target_enemy.x
                        target_pos_y = target_enemy.y
                        should_move = True
                else:
                    target_enemy = min(enemies, key=lambda e: (e.x - self.ball.x) ** 2 + (e.y - self.ball.y) ** 2)
                    target_pos_x = target_enemy.x
                    target_pos_y = target_enemy.y
                    should_move = True

                if should_move:
                    dx, dy = target_pos_x - self.ball.x, target_pos_y - self.ball.y
                    dist_sq = dx * dx + dy * dy
                    if dist_sq > 0.0001:
                        dist = math.sqrt(dist_sq)
                        nx, ny = dx / dist, dy / dist
                        nx, ny = self._apply_obstacle_avoidance(nx, ny, target_enemy)
                        speed = getattr(self.ball, "speed", 2.0)
                        step = speed * 0.5 * delta * 60
                        self.ball.x += nx * min(step, dist)
                        self.ball.y += ny * min(step, dist)

                if target_enemy:
                    # Recalculate distance to enemy for attack
                    dx_e, dy_e = target_enemy.x - self.ball.x, target_enemy.y - self.ball.y
                    dist_e_sq = dx_e * dx_e + dy_e * dy_e
                    dist_e = math.sqrt(dist_e_sq) if dist_e_sq > 0.0001 else 0.0

                    target_radius = getattr(target_enemy, "radius", 10.0)
                    ball_radius = getattr(self.ball, "radius", 10.0)
                    if dist_e <= ball_radius + target_radius + 5:
                        attack_timer = getattr(self.ball, "attack_timer", 0.0)
                        if attack_timer <= 0:
                            if hasattr(self.world, "_deal_damage"):
                                self.world._deal_damage(self.ball, target_enemy)
                                if hasattr(target_enemy, "id") and hasattr(self.ball, "id"):
                                    target_enemy.memory = getattr(target_enemy, "memory", {})
                                    target_enemy.memory[self.ball.id] = {"relation": "rival"}

                            b_type = getattr(self.ball, "ball_type", "").lower()
                            if b_type in ("tank", "juggernaut", "guardian"):
                                cooldown = 1.5
                            else:
                                speed = getattr(self.ball, "speed", 2.0)
                                cooldown = max(0.2, 2.0 / speed if speed > 0 else 1.0)
                            self.ball.attack_timer = cooldown
                return
        elif personality in ("healer", "leader", "caring"):
            allies = self._get_allies()
            target_ally = None
            lowest_hp = 0.8
            for ally in allies:
                ally_hp_pct = 1.0
                if hasattr(ally, "get_hp_percent"):
                    ally_hp_pct = ally.get_hp_percent()
                elif hasattr(ally, "hp") and hasattr(ally, "max_hp"):
                    ally_hp_pct = float(ally.hp) / float(ally.max_hp)

                if ally_hp_pct < lowest_hp:
                    lowest_hp = ally_hp_pct
                    target_ally = ally

            if target_ally:
                dx, dy = target_ally.x - self.ball.x, target_ally.y - self.ball.y
                dist_sq = dx * dx + dy * dy
                if dist_sq > 0.0001:
                    dist = math.sqrt(dist_sq)
                    nx, ny = dx / dist, dy / dist
                    nx, ny = self._apply_obstacle_avoidance(nx, ny, target_ally)
                    speed = getattr(self.ball, "speed", 2.0)
                    step = speed * delta * 60
                    self.ball.x += nx * min(step, dist)
                    self.ball.y += ny * min(step, dist)

                # Recalculate distance after movement
                dx, dy = target_ally.x - self.ball.x, target_ally.y - self.ball.y
                dist_sq = dx * dx + dy * dy
                dist = math.sqrt(dist_sq) if dist_sq > 0.0001 else 0.0

                target_radius = getattr(target_ally, "radius", 10.0)
                ball_radius = getattr(self.ball, "radius", 10.0)
                if dist <= ball_radius + target_radius + 5:
                    attack_timer = getattr(self.ball, "attack_timer", 0.0)
                    if attack_timer <= 0:
                        # Explicit healing logic
                        if hasattr(target_ally, "hp") and hasattr(target_ally, "max_hp"):
                            damage = getattr(self.ball, "damage", 5.0)
                            target_ally.hp = min(target_ally.max_hp, target_ally.hp + (damage * 3.0))

                        if hasattr(self.ball, "use_skill"):
                            self.ball.use_skill()

                        if hasattr(self.ball, "skill_timer") and hasattr(self.ball, "skill_cooldown"):
                            self.ball.skill_timer = self.ball.skill_cooldown

                        b_type = getattr(self.ball, "ball_type", "").lower()
                        if b_type in ("tank", "juggernaut", "guardian"):
                            cooldown = 1.5
                        else:
                            speed = getattr(self.ball, "speed", 2.0)
                            cooldown = max(0.2, 2.0 / speed if speed > 0 else 1.0)
                        self.ball.attack_timer = cooldown
                return

        # Defend fallback
        self._idle(delta * 0.5)

    def _collect_booster(self, delta: float) -> None:
        boosters = self._get_boosters()
        if boosters:
            # Check for nearby enemies to interrupt collection
            enemies = self._get_enemies()
            ball_radius = getattr(self.ball, "radius", 10.0)
            if enemies:
                nearest_enemy = min(enemies, key=lambda e: (e.x - self.ball.x) ** 2 + (e.y - self.ball.y) ** 2)
                enemy_radius = getattr(nearest_enemy, "radius", 10.0)
                dx_enemy = nearest_enemy.x - self.ball.x
                dy_enemy = nearest_enemy.y - self.ball.y
                dist_enemy_sq = dx_enemy * dx_enemy + dy_enemy * dy_enemy
                if dist_enemy_sq > 0.0001:
                    dist_enemy = math.sqrt(dist_enemy_sq)
                    if dist_enemy < ball_radius + enemy_radius + 30.0:
                        self._flee(delta)
                        return

            nearest = min(boosters, key=lambda b: (b.x - self.ball.x) ** 2 + (b.y - self.ball.y) ** 2)
            dx, dy = nearest.x - self.ball.x, nearest.y - self.ball.y
            dist_sq = dx * dx + dy * dy
            if dist_sq > 0.0001:
                dist = math.sqrt(dist_sq)
                nx, ny = dx / dist, dy / dist
                nx, ny = self._apply_obstacle_avoidance(nx, ny, nearest, ignore_enemies=True)
                nx, ny = self._apply_boid_rules(nx, ny)

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

            skill_name = getattr(self.ball, "skill", "")
            if skill_name == "command":
                self.ball.team_message = {"type": "buff_command", "radius": 200}
            elif skill_name in ("Действие", "action_skill"):
                self.ball.team_message = {"type": "action_skill_used", "radius": 150}

            if hasattr(self.ball, "skill_cooldown"):
                self.ball.skill_timer = self.ball.skill_cooldown

    def _idle(self, delta: float) -> None:
        speed = getattr(self.ball, "speed", 2.0)
        nx = random.uniform(-1, 1)
        ny = random.uniform(-1, 1)
        dist_sq = nx*nx + ny*ny
        if dist_sq > 0.0001:
            dist = math.sqrt(dist_sq)
            nx /= dist
            ny /= dist
        else:
            nx, ny = 0.0, 0.0

        nx, ny = self._apply_boid_rules(nx, ny)

        self.ball.x += nx * speed * 0.3
        self.ball.y += ny * speed * 0.3

    def _clamp_position(self) -> bool:
        bounced = False
        radius = getattr(self.ball, "radius", 10.0)

        if math.isnan(self.ball.x) or math.isinf(self.ball.x):
            self.ball.x = getattr(self.world, "width", 1000) / 2
            bounced = True
        if math.isnan(self.ball.y) or math.isinf(self.ball.y):
            self.ball.y = getattr(self.world, "height", 1000) / 2
            bounced = True

        if hasattr(self.world, "arena") and hasattr(self.world.arena, "clamp_position"):
            old_x, old_y = self.ball.x, self.ball.y
            self.ball.x, self.ball.y, bounced_arena = self.world.arena.clamp_position(self.ball.x, self.ball.y, radius)
            if bounced_arena:
                bounced = True
        elif hasattr(self.world, "width") and hasattr(self.world, "height"):
            old_x, old_y = self.ball.x, self.ball.y
            self.ball.x = max(radius, min(self.world.width - radius, self.ball.x))
            self.ball.y = max(radius, min(self.world.height - radius, self.ball.y))
            if old_x != self.ball.x or old_y != self.ball.y:
                bounced = True

        return bounced

    def _resolve_collisions(self) -> bool:
        bounced = False
        ball_radius = getattr(self.ball, "radius", 10.0)
        # Assuming we just need nearby entities to avoid checking everyone
        nearby = []
        if hasattr(self.world, "get_nearby_entities"):
            try:
                # We check a reasonable distance to find overlapping balls
                data = self.world.get_nearby_entities(self.ball, ball_radius * 2)
                if isinstance(data, dict):
                    nearby = data.get("enemies", []) + data.get("allies", [])
                elif isinstance(data, list):
                    nearby = data
            except Exception:
                pass

        for other in nearby:
            if other is self.ball:
                continue
            other_radius = getattr(other, "radius", 10.0)
            dx = self.ball.x - other.x
            dy = self.ball.y - other.y
            dist_sq = dx * dx + dy * dy
            min_dist = ball_radius + other_radius
            if dist_sq < min_dist * min_dist and dist_sq > 0.0001:
                import math
                dist = math.sqrt(dist_sq)
                overlap = min_dist - dist

                # Simple separation, pushing self away
                nx = dx / dist
                ny = dy / dist

                self.ball.x += nx * overlap
                self.ball.y += ny * overlap
                bounced = True

        return bounced

    def _trigger_ripple_effect(self) -> None:
        ball_radius = getattr(self.ball, "radius", 10.0)
        speed = getattr(self.ball, "speed", 2.0)
        ripple_radius = ball_radius * 3.0 + speed * 10.0

        nearby = []
        if hasattr(self.world, "get_nearby_entities"):
            try:
                data = self.world.get_nearby_entities(self.ball, ripple_radius)
                if isinstance(data, dict):
                    nearby = data.get("enemies", []) + data.get("allies", [])
                elif isinstance(data, list):
                    nearby = data
            except Exception:
                pass

        for other in nearby:
            if other is self.ball:
                continue
            dx = other.x - self.ball.x
            dy = other.y - self.ball.y
            dist_sq = dx * dx + dy * dy
            if dist_sq > 0.0001 and dist_sq < ripple_radius * ripple_radius:
                import math
                dist = math.sqrt(dist_sq)
                nx = dx / dist
                ny = dy / dist

                push_strength = (ripple_radius - dist) / ripple_radius * speed * 2.0
                other.x += nx * push_strength
                other.y += ny * push_strength

                # Cause extra damage to enemies if speed is high enough
                if speed > 2.5:
                    is_enemy = getattr(other, "ball_type", "") != getattr(self.ball, "ball_type", "")
                    if is_enemy and hasattr(self.world, "_deal_damage"):
                        self.world._deal_damage(self.ball, other)
                        if hasattr(other, "id") and hasattr(self.ball, "id"):
                            other.memory = getattr(other, "memory", {})
                            other.memory[self.ball.id] = {"relation": "rival"}

    def _update_skill_timer(self, delta: float) -> None:
        if hasattr(self.ball, "skill_timer") and self.ball.skill_timer > 0:
            self.ball.skill_timer -= delta
        if hasattr(self.ball, "attack_timer") and self.ball.attack_timer > 0:
            self.ball.attack_timer -= delta

    def _kite(self, delta: float) -> None:
        enemies = self._get_enemies()
        if enemies:
            target_msg = None
            allies = self._get_allies()
            for ally in allies:
                msg = getattr(ally, "team_message", None)
                if msg and isinstance(msg, dict) and msg.get("type") == "target_spotted":
                    target_msg = msg
                    break

            if target_msg:
                tx, ty = target_msg.get("x", self.ball.x), target_msg.get("y", self.ball.y)
                target = min(enemies, key=lambda e: (e.x - tx) ** 2 + (e.y - ty) ** 2)
            else:
                target = min(enemies, key=lambda e: (e.x - self.ball.x) ** 2 + (e.y - self.ball.y) ** 2)

            if getattr(self.ball, "team_message", None) is None:
                self.ball.team_message = {"type": "target_spotted", "x": target.x, "y": target.y}

            dx, dy = target.x - self.ball.x, target.y - self.ball.y
            dist_sq = dx * dx + dy * dy
            if dist_sq > 0.0001:
                dist = math.sqrt(dist_sq)
                nx, ny = dx / dist, dy / dist

                attack_range = getattr(self.ball, "attack_range", 150.0)

                if dist > attack_range:
                    pass # Move towards
                elif dist < attack_range * 0.8:
                    nx, ny = -nx, -ny # Kite away
                else:
                    nx, ny = 0.0, 0.0 # Maintain distance

                if nx != 0.0 or ny != 0.0:
                    nx, ny = self._apply_obstacle_avoidance(nx, ny, target)
                    nx, ny = self._apply_boid_rules(nx, ny)

                    step = getattr(self.ball, "speed", 2.0) * delta * 60
                    if dist < attack_range * 0.8:
                        self.ball.x += nx * step
                        self.ball.y += ny * step
                    else:
                        self.ball.x += nx * min(step, dist)
                        self.ball.y += ny * min(step, dist)

            # Recalculate distance after movement
            dx, dy = target.x - self.ball.x, target.y - self.ball.y
            dist_sq = dx * dx + dy * dy
            dist = math.sqrt(dist_sq) if dist_sq > 0.0001 else 0.0
            dist_after = dist

            attack_range = getattr(self.ball, "attack_range", 150.0)

            if dist_after <= attack_range:
                # Uses skill when available and optimal
                skill_timer = getattr(self.ball, "skill_timer", 0.0)
                if skill_timer <= 0:
                    if dist_after < attack_range * 0.8:
                        if hasattr(self.ball, "use_skill"):
                            self.ball.use_skill()
                        self.ball.skill_timer = getattr(self.ball, "skill_cooldown", 5.0)

                # Deal damage with attack timer
                attack_timer = getattr(self.ball, "attack_timer", 0.0)
                if attack_timer <= 0:
                    if hasattr(self.world, "_deal_damage"):
                        self.world._deal_damage(self.ball, target)
                        if hasattr(target, "id") and hasattr(self.ball, "id"):
                            # Rivalry memory update
                            if not hasattr(target, "memory"):
                                target.memory = {}
                            target.memory[self.ball.id] = {"relation": "rival"}

                    speed = getattr(self.ball, "speed", 2.0)
                    cooldown = max(0.2, 2.0 / speed if speed > 0 else 1.0)
                    self.ball.attack_timer = cooldown
        else:
            self._idle(delta)
