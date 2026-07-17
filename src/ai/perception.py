import math
from typing import Any, Dict

class Perception:
    """
    Perception system that scans the world for nearby entities:
    enemies, allies, boosters, and traps.
    Calculates distances, threat levels, and opportunity scores.
    """

    def __init__(self, ball: Any, world: Any):
        self.ball = ball
        self.world = world

    def scan(self) -> Dict[str, Any]:
        """
        Scans the environment within the ball's perception radius.
        Returns a dictionary with entities, distances, and scores.
        """
        perception_radius = getattr(self.ball, "perception_radius", 300.0)

        # Global cosmetics string for checks
        cosmetic_val = str(getattr(self.ball, "cosmetic", "")).lower().replace(" ", "_")

        has_sonar = getattr(self.ball, "sonar_ping_timer", 0.0) > 0
        if has_sonar:
            perception_radius = max(perception_radius, 1500.0)


        is_lunar = hasattr(self.world, "arena") and getattr(self.world.arena, "is_lunar_eclipse", False)
        if is_lunar:
            perception_radius = 999999.0


        if hasattr(self.world, "arena") and getattr(self.world.arena, "is_night", None) is not None:
            # Check for active flares in the arena
            has_flare_vision = False
            if hasattr(self.world.arena, "hazards"):
                bx = getattr(self.ball, "x", 0)
                by = getattr(self.ball, "y", 0)
                for h in self.world.arena.hazards:
                    if getattr(h, "kind", "") == "flare" and getattr(h, "active", True):
                        fx = getattr(h, "x", 0)
                        fy = getattr(h, "y", 0)
                        fr = getattr(h, "radius", 0)
                        if (bx - fx)**2 + (by - fy)**2 <= fr**2:
                            has_flare_vision = True
                            break

            has_night_vision = False
            if hasattr(self.ball, "traits") and "night_vision" in self.ball.traits:
                has_night_vision = True
            if getattr(self.ball, "ball_type", "") == "vampire":
                has_night_vision = True
            if cosmetic_val in ["night_vision_goggles", "lantern", "thermal_goggles", "infrared_goggles"]:
                has_night_vision = True
            if getattr(self.ball, "has_thermal_vision", False):
                has_night_vision = True
            if getattr(self.ball, "light_source_booster_timer", 0.0) > 0:
                has_night_vision = True

            # Dynamic vision enhancements based on items and cosmetics
            has_thermal_vision = getattr(self.ball, "has_thermal_vision", False) or cosmetic_val in ["thermal_goggles", "infrared_goggles"]
            if has_thermal_vision and getattr(self.world.arena, 'is_night', False):
                perception_radius = max(perception_radius, 1000.0)
            has_advanced_optics = getattr(self.ball, "advanced_optics_active", False)
            if has_advanced_optics:
                perception_radius = max(perception_radius, 1500.0)

            if getattr(self.world.arena, "is_lunar_eclipse", False):
                perception_radius = max(perception_radius, 2000.0)
            elif getattr(self.world.arena, "is_eclipse", False):
                perception_radius = min(perception_radius, 20.0)
            elif has_flare_vision:
                perception_radius = max(perception_radius, 2000.0)
            elif getattr(self.world.arena, 'is_night', False):
                if not has_night_vision:
                    night_ratio = getattr(self.world.arena, "night_ratio", 1.0)
                    perception_radius = max(100.0, perception_radius * (1.0 - night_ratio * 0.8))
            else:
                perception_radius = max(perception_radius, 2000.0)

        is_lunar = hasattr(self.world, "arena") and getattr(self.world.arena, "is_lunar_eclipse", False)

        has_thermal_vision = getattr(self.ball, "has_thermal_vision", False) or cosmetic_val in ["thermal_goggles", "infrared_goggles", "vision_module"]

        ignores_fog = has_thermal_vision or cosmetic_val == "thermal_goggles"
        ignores_sandstorm = has_thermal_vision or cosmetic_val in ["desert_goggles", "sand_goggles"]
        ignores_snow = has_thermal_vision or cosmetic_val in ["snow_goggles", "ski_goggles"]
        ignores_rain = has_thermal_vision or cosmetic_val in ["rain_goggles", "waterproof_goggles"]
        ignores_windy = has_thermal_vision

        if hasattr(self.world, "arena") and getattr(self.world.arena, "is_foggy", None) is not None:
            if self.world.arena.is_foggy and not ignores_fog and not is_lunar:
                perception_radius = min(perception_radius, 80.0)
        if hasattr(self.world, "arena") and getattr(self.world.arena, "is_raining", None) is not None:
            if self.world.arena.is_raining and not ignores_rain and not is_lunar:
                perception_radius = perception_radius * 0.8
        if hasattr(self.world, "arena") and getattr(self.world.arena, "is_windy", None) is not None:
            if self.world.arena.is_windy and not ignores_windy and not is_lunar:
                perception_radius = perception_radius * 0.7
        if hasattr(self.world, "arena") and getattr(self.world.arena, "is_sandstorming", None) is not None:
            if self.world.arena.is_sandstorming and not ignores_sandstorm and getattr(self.ball, "ball_type", "") != "sand_elemental" and not is_lunar:
                perception_radius = perception_radius * 0.3
        if hasattr(self.world, "arena") and getattr(self.world.arena, "is_snowing", None) is not None:
            if self.world.arena.is_snowing and not ignores_snow and getattr(self.ball, "ball_type", "") != "snow_yeti" and not is_lunar:
                perception_radius = perception_radius * 0.6

        data: Dict[str, Any] = {
            "enemies": [],
            "allies": [],
            "boosters": [],
            "traps": [],
            "distances": {}, # Maps entity id to distance
            "threat_level": 0.0,
            "opportunity_score": 0.0,
            "coach_strategy": "",
            # For backward compatibility with existing layers
            "danger_level": 0.0,
            "opportunity_level": 0.0,
            "rival_spotted": False,
        }

        if not self.world or not hasattr(self.world, "get_nearby_entities"):
            return data

        in_smoke = False
        smoke_hazards = []
        bx_curr, by_curr = getattr(self.ball, "x", 0), getattr(self.ball, "y", 0)
        if hasattr(self.world, "arena") and hasattr(self.world.arena, "hazards"):
            for h in self.world.arena.hazards:
                if getattr(h, "kind", "") in ["smokescreen", "breakable_wall"]:
                    smoke_hazards.append(h)
                    dist = math.sqrt((getattr(h, "x", 0) - bx_curr)**2 + (getattr(h, "y", 0) - by_curr)**2)
                    if dist <= getattr(h, "radius", 0):
                        in_smoke = True
        has_thermal = getattr(self.ball, "has_thermal_vision", False) or cosmetic_val in ["thermal_goggles", "infrared_goggles"]
        if in_smoke and not has_thermal:
            perception_radius = min(perception_radius, 50.0)

        entities = self.world.get_nearby_entities(self.ball, perception_radius)
        def intersects_smoke(ent):
            if has_sonar:
                return False
            has_thermal_internal = getattr(self.ball, "has_thermal_vision", False) or cosmetic_val in ["thermal_goggles", "infrared_goggles"]
            if has_thermal_internal:
                return False
            ex, ey = getattr(ent, "x", 0), getattr(ent, "y", 0)
            for h in smoke_hazards:
                hx, hy, hr = getattr(h, "x", 0), getattr(h, "y", 0), getattr(h, "radius", 0)
                dx = ex - bx_curr
                dy = ey - by_curr
                l2 = dx*dx + dy*dy
                if l2 == 0:
                    dist = math.sqrt((hx - bx_curr)**2 + (hy - by_curr)**2)
                else:
                    t = max(0, min(1, ((hx - bx_curr) * dx + (hy - by_curr) * dy) / l2))
                    px = bx_curr + t * dx
                    py = by_curr + t * dy
                    dist = math.sqrt((hx - px)**2 + (hy - py)**2)
                if dist <= hr:
                    return True
            return False



        # Apply stealth drone logic for enemies detecting us, or us detecting enemies
        filtered_enemies = []
        active_flares = []
        if hasattr(self.world, "arena") and hasattr(self.world.arena, "hazards"):
            active_flares = [h for h in self.world.arena.hazards if getattr(h, "kind", "") == "flare" and getattr(h, "active", True)]

        # Determine if ball has thermal vision to detect invisible hazards/entities
        has_thermal_vision = getattr(self.ball, "has_thermal_vision", False) or cosmetic_val in ["thermal_goggles", "infrared_goggles"]

        for e in entities.get("enemies", []):
            if getattr(e, "underground", False): continue
            if intersects_smoke(e):
                continue

            if has_sonar:
                filtered_enemies.append(e)
                continue

            # Check if enemy is revealed by flare
            revealed_by_flare = False
            ex = getattr(e, "x", 0)
            ey = getattr(e, "y", 0)
            for f in active_flares:
                fx = getattr(f, "x", 0)
                fy = getattr(f, "y", 0)
                fr = getattr(f, "radius", 0)
                if (ex - fx)**2 + (ey - fy)**2 <= fr**2:
                    revealed_by_flare = True
                    break

            if not revealed_by_flare:
                # If enemy has stealth drone, we can only see them if they are very close
                e_has_stealth = getattr(e, "has_stealth_drone", False)
                if not e_has_stealth and hasattr(e, "has_method") and e.has_method("get_meta") and e.has_meta("has_stealth_drone"):
                    e_has_stealth = e.get_meta("has_stealth_drone")

                e_has_shadow = False
                if hasattr(e, "has_method") and e.has_method("get_meta") and e.has_meta("shadow_booster_timer"):
                    e_has_shadow = e.get_meta("shadow_booster_timer") > 0
                elif hasattr(e, "shadow_booster_timer"):
                    e_has_shadow = e.shadow_booster_timer > 0

                e_has_stealth_booster = False
                if hasattr(e, "has_method") and e.has_method("get_meta") and e.has_meta("stealth_booster_timer"):
                    e_has_stealth_booster = e.get_meta("stealth_booster_timer") > 0
                elif hasattr(e, "stealth_booster_timer"):
                    e_has_stealth_booster = e.stealth_booster_timer > 0
                e_has_ghost_mode_booster = False
                if hasattr(e, "has_method") and e.has_method("get_meta") and e.has_meta("ghost_mode_active"):
                    e_has_ghost_mode_booster = e.get_meta("ghost_mode_active")
                elif hasattr(e, "ghost_mode_active"):
                    e_has_ghost_mode_booster = e.ghost_mode_active

                is_sand_cloaked = False
                if getattr(e, "ball_type", "") == "sand_elemental" and hasattr(self.world, "arena") and getattr(self.world.arena, "is_sandstorming", False):
                    is_sand_cloaked = True

                if e_has_stealth or e_has_shadow or is_sand_cloaked or e_has_stealth_booster or e_has_ghost_mode_booster:
                    dist = math.sqrt((ex - bx_curr)**2 + (ey - by_curr)**2)

                    if has_thermal_vision:
                        # Thermal vision bypasses most cloaking up to a certain range
                        if dist > 500.0:
                            continue
                    else:
                        if (e_has_stealth_booster or e_has_ghost_mode_booster) and dist > 15.0:
                            continue
                        elif is_sand_cloaked and dist > 40.0:
                            continue
                        elif e_has_shadow and dist > 30.0:
                            continue
                        elif e_has_stealth and dist > 80.0:
                            continue
            filtered_enemies.append(e)

        data["enemies"] = filtered_enemies
        data["allies"] = [e for e in entities.get("allies", []) if not intersects_smoke(e) and not getattr(e, "underground", False)]
        data["boosters"] = [e for e in entities.get("boosters", []) if not intersects_smoke(e)]
        data["traps"] = [e for e in entities.get("traps", []) if not intersects_smoke(e)]

        # Calculate distances and scores
        threat = 0.0
        opp = 0.0

        bx, by = getattr(self.ball, "x", 0), getattr(self.ball, "y", 0)

        # Helper to compute distance
        def calc_dist(ent):
            ex, ey = getattr(ent, "x", 0), getattr(ent, "y", 0)
            dx = ex - bx
            dy = ey - by
            return math.sqrt(dx * dx + dy * dy)

        # Include procedural hazards within perception radius
        if hasattr(self.world, "arena") and hasattr(self.world.arena, "hazards"):
            import random
            for h in self.world.arena.hazards:
                dist = calc_dist(h)
                # Check if within perception radius and not already in traps
                if dist <= perception_radius:
                    if getattr(h, "kind", "") == "fake_booster":
                        is_scout = getattr(self.ball, "ball_type", "") == "scout"
                        has_drone = getattr(self.ball, "has_drone", False)
                        perception_score = getattr(self.ball, "perception_score", 0.0)

                        identified = False
                        if is_scout:
                            if perception_score > 50 or random.random() < 0.3:
                                identified = True

                        if has_drone:
                            identified = True

                        if identified:
                            if not any(getattr(t, "id", None) == getattr(h, "id", None) for t in data["traps"]):
                                data["traps"].append(h)
                        else:
                            if not any(getattr(b, "id", None) == h.id for b in data["boosters"]):
                                data["boosters"].append(h)
                    else:
                        # Make sure it's not already in there by id
                        if getattr(h, "kind", "") == "drone_item" or getattr(h, "kind", "") == "stealth_drone_item" or getattr(h, "kind", "") == "shadow_booster" or getattr(h, "kind", "") == "stealth_booster":
                            if not any(getattr(b, "id", None) == h.id for b in data["boosters"]):
                                data["boosters"].append(h)
                        else:
                            if not any(getattr(t, "id", None) == getattr(h, "id", None) for t in data["traps"]):
                                data["traps"].append(h)

        for enemy in data["enemies"]:
            dist = calc_dist(enemy)
            if hasattr(enemy, "id"):
                data["distances"][enemy.id] = dist

                # Ball Relationships - Balls remember each other


                # Rivalry skill: attacked me before -> attack on sight
                if hasattr(self.ball, "memory"):
                    ball_mem = self.ball.memory.get(enemy.id, {})
                    if ball_mem.get("relation") == "rival":
                        data["rival_spotted"] = True

            # Threat increases if enemy is closer. Max threat from one enemy = 1.0 (at dist 0)
            threat += max(0.0, 1.0 - (dist / perception_radius)) * 1.5 if perception_radius > 0 else 0.0

        for trap in data["traps"]:
            dist = calc_dist(trap)
            if hasattr(trap, "id"):
                data["distances"][trap.id] = dist
            threat += max(0.0, 1.0 - (dist / perception_radius)) * 2.0 if perception_radius > 0 else 0.0

        for booster in data["boosters"]:
            dist = calc_dist(booster)
            if hasattr(booster, "id"):
                data["distances"][booster.id] = dist
            opp += max(0.0, 1.0 - (dist / perception_radius)) * 1.0 if perception_radius > 0 else 0.0

        team_messages = []

        for ally in data["allies"]:
            dist = calc_dist(ally)
            if hasattr(ally, "id"):
                data["distances"][ally.id] = dist
            opp += max(0.0, 1.0 - (dist / perception_radius)) * 0.5 if perception_radius > 0 else 0.0
            if hasattr(ally, "team_message") and ally.team_message:
                team_messages.append(ally.team_message)

        data["threat_level"] = threat
        data["opportunity_score"] = opp

        # Coach Mode
        if hasattr(self.world, "coach_strategy") and self.world.coach_strategy:
            strat = self.world.coach_strategy
            if isinstance(strat, dict):
                team = getattr(self.ball, "team", getattr(self.ball, "ball_type", ""))
                if team in strat:
                    data["coach_strategy"] = strat[team]
            elif isinstance(strat, str):
                data["coach_strategy"] = strat


        # Backward compatibility for existing logic
        data["danger_level"] = len(data["enemies"]) * 0.2
        data["opportunity_level"] = len(data["boosters"]) * 0.3 + len(data["allies"]) * 0.1
        data["team_messages"] = team_messages

        return data
