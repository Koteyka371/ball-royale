from typing import Dict, List, Any
import random

class CrowdSystem:
    def __init__(self, world):
        self.world = world
        self.excitement_level = 0.0
        self.corruptibility_level = 0.5
        self.max_excitement = 100.0
        self.team_alive_counts = {}
        self.active_vote = None
        self.votes = {}
        self.vote_timer = 0
        self.vote_cooldown = 0
        self.active_global_modifier = None
        self.global_modifier_timer = 0
        self.last_kill_tick = 0
        self.kill_streak = {}
        self.ball_positions = {}
        self.camping_time = {}
        self.underdog_team = None
        self.match_started = False
        self.match_ended = False
        self.external_commands = []
        self.consecutive_chants = 0
        self.last_chant_team = None
        self.has_real_spectators = False
        self.viewer_loyalty = {}
        self.user_votes = {}

    def _add_viewer_loyalty(self, user: str, points: int):
        self.viewer_loyalty[user] = self.viewer_loyalty.get(user, 0) + points
        if hasattr(self, 'world') and hasattr(self.world, 'leaderboard_manager'):
            if hasattr(self.world.leaderboard_manager, 'record_viewer_loyalty'):
                self.world.leaderboard_manager.record_viewer_loyalty(user, points)

    def _get_user_display(self, user: str) -> str:
        badge = ""
        if hasattr(self, 'world') and hasattr(self.world, 'leaderboard_manager') and hasattr(self.world.leaderboard_manager, 'get_viewer_badge'):
            badge = self.world.leaderboard_manager.get_viewer_badge(user)
        else:
            points = self.viewer_loyalty.get(user, 0)
            if points >= 50:
                badge = "👑"
            elif points >= 20:
                badge = "⭐"

        if badge:
            return f"{badge} {user}"
        return user

    def queue_external_command(self, user: str, command: str):
        if not hasattr(self, 'external_commands'):
            self.external_commands = []
        self.external_commands.append((user, command))
        self.has_real_spectators = True

    def process_external_command(self, user: str, command: str, balls: 'List[Any]'):
        parts = command.strip().split()
        if not parts:
            return

        cmd = parts[0].lower()
        alive_balls = [b for b in balls if getattr(b, "alive", False) and getattr(b, "ball_type", "") != "spectator"]

        if cmd == "!spawn" and len(parts) >= 2:
            hazard_kind = parts[1]
            target = None
            if len(parts) >= 3:
                try:
                    tid = int(parts[2])
                    target = next((b for b in alive_balls if getattr(b, "id", -1) == tid), None)
                except ValueError:
                    pass
            if not target and alive_balls:
                target = random.choice(alive_balls)

            if target and hasattr(self.world, 'add_event'):
                self.world.add_event("spawn_hazard", {
                    "x": getattr(target, "x", 0),
                    "y": getattr(target, "y", 0),
                    "kind": hazard_kind
                })
                self._add_viewer_loyalty(user, 5)
                self.world.add_event("crowd_throw", {"message": f"Viewer {self._get_user_display(user)} spawned a {hazard_kind}!"})
                self.excitement_level += 5.0

        elif cmd == "!control" and len(parts) >= 4:
            hazard_kind = parts[1]
            try:
                target_x = float(parts[2])
                target_y = float(parts[3])

                # Find hazard
                if hasattr(self.world, 'arena') and hasattr(self.world.arena, 'hazards'):
                    matching_hazards = [h for h in self.world.arena.hazards if getattr(h, "kind", "") == hazard_kind]
                    if matching_hazards:
                        hazard = random.choice(matching_hazards)
                        hazard.controlled_by = user
                        hazard.control_timer = 10.0 # 10 seconds of control
                        hazard.control_target_x = target_x
                        hazard.control_target_y = target_y

                        self._add_viewer_loyalty(user, 15)
                        if hasattr(self.world, 'add_event'):
                            self.world.add_event("crowd_cheer", {"message": f"Viewer {self._get_user_display(user)} took control of a {hazard_kind}!"})
                            self.excitement_level += 10.0
            except ValueError:
                pass
        elif cmd == "!weather" and len(parts) >= 2:
            if self.excitement_level >= 50.0:
                weather_type = parts[1].lower()
                if weather_type in ["hot", "heatwave"]:
                    if hasattr(self.world, 'arena') and hasattr(self.world.arena, 'temperature'):
                        self.world.arena.temperature = 50.0
                    if hasattr(self.world, 'add_event'):
                        self.world.add_event("arena_modifier", {"temperature": 50.0})
                        self._add_viewer_loyalty(user, 10)
                        self.world.add_event("crowd_cheer", {"message": f"Viewer {self._get_user_display(user)} made it HOT!"})
                elif weather_type in ["cold", "blizzard", "snow"]:
                    if hasattr(self.world, 'arena') and hasattr(self.world.arena, 'temperature'):
                        self.world.arena.temperature = -20.0
                    if hasattr(self.world, 'add_event'):
                        self.world.add_event("arena_modifier", {"temperature": -20.0})
                        self._add_viewer_loyalty(user, 10)
                        self.world.add_event("crowd_cheer", {"message": f"Viewer {self._get_user_display(user)} made it COLD!"})
                else:
                    if hasattr(self.world, 'add_event'):
                        target = None
                        if alive_balls:
                            target = random.choice(alive_balls)
                        if target:
                            self.world.add_event("spawn_hazard", {
                                "x": getattr(target, "x", 0),
                                "y": getattr(target, "y", 0),
                                "kind": weather_type
                            })
                            self._add_viewer_loyalty(user, 10)
                            self.world.add_event("crowd_cheer", {"message": f"Viewer {self._get_user_display(user)} summoned a {weather_type}!"})
                self.excitement_level -= 10.0

        elif cmd == "!drop" and len(parts) >= 2:
            booster_kind = parts[1]
            target = None
            if len(parts) >= 3:
                try:
                    tid = int(parts[2])
                    target = next((b for b in alive_balls if getattr(b, "id", -1) == tid), None)
                except ValueError:
                    pass
            if not target and alive_balls:
                target = random.choice(alive_balls)

            if target and hasattr(self.world, 'add_event'):
                self.world.add_event("spawn_booster", {
                    "x": getattr(target, "x", 0),
                    "y": getattr(target, "y", 0),
                    "kind": booster_kind,
                    "value": 30.0
                })
                self._add_viewer_loyalty(user, 5)
                self.world.add_event("crowd_throw", {"message": f"Viewer {self._get_user_display(user)} dropped a {booster_kind} booster!"})
                self.excitement_level += 5.0

        elif cmd == "!emote" and len(parts) >= 2:
            emote_type = parts[1]
            target = None
            if len(parts) >= 3:
                try:
                    tid = int(parts[2])
                    target = next((b for b in alive_balls if getattr(b, "id", -1) == tid), None)
                except ValueError:
                    pass
            if not target and alive_balls:
                target = random.choice(alive_balls)

            if target and hasattr(self.world, 'add_event'):
                self.world.add_event("spawn_hazard", {
                    "x": getattr(target, "x", 0),
                    "y": getattr(target, "y", 0),
                    "kind": "emote",
                    "emoji": emote_type
                })
                self._add_viewer_loyalty(user, 5)
                self.world.add_event("crowd_throw", {"message": f"Viewer {self._get_user_display(user)} spawned a {emote_type} emote!"})
                self.excitement_level += 2.0

        elif cmd == "!vote" and len(parts) >= 2:
            option = parts[1]
            if getattr(self, 'active_vote', None) and getattr(self, 'votes', None) is not None:
                self.user_votes[user] = option
                if option in self.votes:
                    self.votes[option] += 1
                else:
                    self.votes[option] = 1
                if hasattr(self.world, 'add_event'):
                    self.world.add_event("crowd_cheer", {"message": f"Viewer {self._get_user_display(user)} voted for {option}!"})

        elif cmd == "!bounty" and len(parts) >= 2:
            target_id = None
            try:
                target_id = int(parts[1])
            except ValueError:
                target_id = parts[1]

            target = next((b for b in alive_balls if str(getattr(b, "id", "")) == str(target_id)), None)
            if target:
                target.crowd_bounty_timer = 600
                if hasattr(self.world, 'add_event'):
                    self.world.add_event("visual_effect", {"type": "bounty_mark", "target_id": getattr(target, 'id', -1)})
                    b_type = getattr(target, 'ball_type', 'Player')
                    self.world.add_event("crowd_cheer", {"message": f"Viewer {self._get_user_display(user)} placed a bounty on {b_type} {target_id}!"})
                self.excitement_level += 10.0

        elif cmd == "!bribe" and len(parts) >= 2:
            action = parts[1]
            option = parts[2] if len(parts) >= 3 else None
            self.player_bribe_vote(user, action, option)

    def player_bribe_vote(self, player_id: str, action: str, option: str = None) -> bool:
        if not self.active_vote or not self.votes:
            return False

        pm = None
        if hasattr(self.world, "get_profile_manager"):
            pm = self.world.get_profile_manager()
        elif hasattr(self.world, "profile_manager"):
            pm = self.world.profile_manager

        if not pm or not hasattr(pm, "data"):
            return False

        currency_type = "skill_points"
        currency_cost = max(10, int(50 * (2.0 - self.corruptibility_level * 1.5)))

        if pm.data.get("skill_points", 0) >= currency_cost:
            pm.data["skill_points"] -= currency_cost
        elif pm.data.get("prestige_tokens", 0) >= 1:
            pm.data["prestige_tokens"] -= 1
            currency_cost = 1
            currency_type = "prestige_tokens"
        else:
            return False

        if action == "cancel":
            if hasattr(self.world, 'add_event'):
                self.world.add_event("vote_cancelled", {"message": f"Player {player_id} bribed the crowd to cancel the vote!"})
            self.active_vote = None
            self.votes = {}
            self.vote_cooldown = 1000
            return True
        elif action == "skew" and option in self.votes:
            self.votes[option] += 5
            if hasattr(self.world, 'add_event'):
                self.world.add_event("crowd_cheer", {"message": f"Player {player_id} bribed the crowd to favor {option}!"})
            return True

        if currency_type == "skill_points":
            pm.data["skill_points"] += 50
        else:
            pm.data["prestige_tokens"] += 1
        return False

    def _process_external_commands(self, balls: 'List[Any]'):
        if not hasattr(self, 'external_commands'):
            self.external_commands = []
        while self.external_commands:
            user, command = self.external_commands.pop(0)
            self.process_external_command(user, command, balls)

    def tick(self, balls: List[Any], kill_log: List[Dict[str, Any]], tick: int):
        self._process_external_commands(balls)
        self._check_bets_and_winner(balls, tick)
        self._update_corruptibility(tick)
        self._update_excitement(tick)
        # Decrement bounty timers
        for b in balls:
            if getattr(b, "crowd_bounty_timer", 0) > 0:
                b.crowd_bounty_timer -= 1

        self._check_events(balls, kill_log, tick)
        self._check_camping(balls, tick)
        self._throw_buffs_if_needed(balls, tick)
        self._throw_hazards_if_bored(balls, tick)
        self._process_audience_favor(balls, tick)
        self._process_votes(balls, tick)
        self._process_spectator_signs(balls, tick)
        self._process_global_modifier(balls, tick)
        self._trigger_large_scale_event(balls, tick)


    def _trigger_large_scale_event(self, balls: List[Any], tick: int):
        if self.excitement_level >= 10.0:
            return

        if random.random() < 0.005:  # 0.5% chance per tick when excitement is critically low
            event_type = random.choice(["closing_zone", "weather_transition"])

            if hasattr(self.world, 'add_event'):
                if event_type == "closing_zone":
                    self.world.add_event("spawn_zone", {
                        "x": 500.0,
                        "y": 500.0,
                        "radius": 1000.0,
                        "shrink_rate": 10.0,
                        "damage": 5.0
                    })
                    self.world.add_event("crowd_throw", {"message": "The crowd is bored! A shrinking zone has been deployed!"})
                else:
                    new_weather = random.choice(["thunderstorm", "blizzard", "acid_rain"])
                    self.world.add_event("weather_transition", {"new_weather": new_weather})
                    self.world.add_event("crowd_throw", {"message": f"The crowd is falling asleep! They trigger a {new_weather}!"})

                self.excitement_level += 40.0

    def _check_camping(self, balls: List[Any], tick: int):
        for b in balls:
            if getattr(b, "alive", False) and getattr(b, "ball_type", "") != "spectator":
                b_id = getattr(b, "id", -1)
                b_x = getattr(b, "x", 0.0)
                b_y = getattr(b, "y", 0.0)

                if b_id in self.ball_positions:
                    old_x, old_y = self.ball_positions[b_id]
                    dist_sq = (b_x - old_x) ** 2 + (b_y - old_y) ** 2

                    if dist_sq < 10.0:
                        self.camping_time[b_id] = self.camping_time.get(b_id, 0) + 1
                    else:
                        self.camping_time[b_id] = 0
                        self.ball_positions[b_id] = (b_x, b_y)

                    if self.camping_time[b_id] >= 50:
                        if hasattr(self.world, 'add_event'):
                            self.world.add_event("crowd_throw", {"message": "The crowd boos and throws debris at a camper!"})
                            self.world.add_event("spawn_hazard", {"x": b_x, "y": b_y, "kind": "spike_trap"})
                        self.camping_time[b_id] = 0
                else:
                    self.ball_positions[b_id] = (b_x, b_y)
                    self.camping_time[b_id] = 0

    def _check_bets_and_winner(self, balls: List[Any], tick: int):
        if not self.match_started and len(balls) > 1:
            self.match_started = True
            teams = {}
            for b in balls:
                team = getattr(b, "team", getattr(b, "ball_type", "unknown"))
                if team != "spectator":
                    teams[team] = teams.get(team, 0) + 1

            if len(teams) > 1:
                # Underdog is the team with the minimum count
                self.underdog_team = min(teams, key=teams.get)
                if hasattr(self.world, "add_event"):
                    self.world.add_event("crowd_bet", {"message": f"The crowd predicts a tough match for the underdog, {self.underdog_team}!"})

        if self.match_started and not self.match_ended:
            alive_teams = set()
            for b in balls:
                if getattr(b, "alive", False):
                    team = getattr(b, "team", getattr(b, "ball_type", "unknown"))
                    if team != "spectator":
                        alive_teams.add(team)

            if len(alive_teams) == 1:
                self.match_ended = True
                winner = list(alive_teams)[0]
                if winner == self.underdog_team:
                    self.excitement_level += 50.0
                    if hasattr(self.world, "add_event"):
                        self.world.add_event("crowd_cheer", {"message": f"The underdog {winner} has won! The crowd goes absolutely WILD!", "volume": 1.5})
                        self.world.add_event("audio_event", {"sound": "epic_crowd_roar", "volume": 1.0})

                    if hasattr(self.world, "profile_manager"):
                        try:
                            pm = self.world.profile_manager
                            if hasattr(pm, "data"):
                                pm.data["prestige_tokens"] = pm.data.get("prestige_tokens", 0) + 10
                                if hasattr(pm, "save"):
                                    pm.save()
                        except Exception:
                            pass



    def _update_corruptibility(self, tick: int):
        import math
        self.corruptibility_level = (math.sin(tick * 0.005) + 1.0) / 2.0

    def _update_excitement(self, tick: int):
        # Decay excitement slowly
        if self.excitement_level > 0:
            self.excitement_level -= 0.05
        self.excitement_level = max(0.0, min(self.excitement_level, self.max_excitement))

    def _check_events(self, balls: List[Any], kill_log: List[Dict[str, Any]], tick: int):
        # We need to only process new kill logs.
        # A simple way is to just look at the last few kills.
        if not kill_log:
            return

        latest_kill = kill_log[-1]
        if latest_kill.get("tick", 0) > self.last_kill_tick:
            self.last_kill_tick = latest_kill["tick"]
            self._handle_kill(latest_kill, tick, balls)

        # Leading team chant (randomly during events if excitement is high)
        if self.excitement_level >= 50.0 and tick % 200 == 0:
            alive_teams = {}
            for b in balls:
                if getattr(b, "alive", False) and getattr(b, "ball_type", "") != "spectator":
                    team = getattr(b, "team", getattr(b, "ball_type", ""))
                    alive_teams[team] = alive_teams.get(team, 0) + 1
            if alive_teams:
                leading_team = max(alive_teams, key=alive_teams.get)
                if alive_teams[leading_team] >= 2 and hasattr(self.world, 'add_event'):
                    self.world.add_event("crowd_cheer", {"message": f"Let's go Team {leading_team}! Let's go!", "volume": 1.0})
                    self.world.add_event("audio_event", {"sound": "team_chant", "volume": 0.8})

                    # Track consecutive chants for Adrenaline buff
                    if not hasattr(self, 'last_chant_team'):
                        self.last_chant_team = leading_team
                        self.consecutive_chants = 1
                    elif self.last_chant_team == leading_team:
                        self.consecutive_chants += 1
                    else:
                        if self.consecutive_chants > 0 and hasattr(self.world, 'add_event'):
                            self.world.add_event("audio_event", {"sound": "bgm_tempo_reset", "volume": 1.0})
                        self.last_chant_team = leading_team
                        self.consecutive_chants = 1

                    self.world.add_event("audio_event", {"sound": "bgm_tempo_up", "volume": 1.0, "speed_multiplier": 1.0 + (self.consecutive_chants * 0.1)})

                    # If 3 or more consecutive chants, apply Adrenaline buff
                    if self.consecutive_chants >= 3:
                        self.world.add_event("crowd_cheer", {"message": f"Team {leading_team} is fueled by the crowd's energy! Adrenaline buff applied!", "volume": 1.2})
                        self.world.add_event("audio_event", {"sound": "adrenaline_rush", "volume": 1.0})
                        self.world.add_event("visual_effect", {"type": "chant_streak", "team": leading_team})
                        for b in balls:
                            if getattr(b, "alive", False) and getattr(b, "team", getattr(b, "ball_type", "")) == leading_team:
                                self.world.add_event("visual_effect", {"type": "adrenaline_buff", "target_id": getattr(b, "id", -1)})
                                self.world.add_event("spawn_booster", {
                                    "x": getattr(b, "x", 0),
                                    "y": getattr(b, "y", 0),
                                    "kind": "speed",
                                    "value": 50.0
                                })
                else:
                    if self.consecutive_chants > 0 and hasattr(self.world, 'add_event'):
                        self.world.add_event("audio_event", {"sound": "bgm_tempo_reset", "volume": 1.0})
                    self.last_chant_team = None
                    self.consecutive_chants = 0
        elif tick % 200 == 0:
            if self.consecutive_chants > 0 and hasattr(self.world, 'add_event'):
                self.world.add_event("audio_event", {"sound": "bgm_tempo_reset", "volume": 1.0})
            self.last_chant_team = None
            self.consecutive_chants = 0

    def _handle_kill(self, kill_info: Dict, tick: int, balls: List[Any]):
        killer_id = kill_info.get("killer_id")
        victim_id = kill_info.get("victim_id")

        victim_obj = next((b for b in balls if getattr(b, "id", -1) == victim_id), None)
        killer_obj = next((b for b in balls if getattr(b, "id", -1) == killer_id), None)

        if victim_obj and killer_obj and getattr(victim_obj, "crowd_bounty_timer", 0) > 0:
            killer_obj.score = getattr(killer_obj, 'score', 0) + 1000
            killer_obj.xp = getattr(killer_obj, 'xp', 0) + 500
            if hasattr(self.world, 'add_event'):
                self.world.add_event("visual_effect", {"type": "bounty_claimed", "target_id": killer_id})
                self.world.add_event("crowd_cheer", {"message": f"The crowd goes wild as a bounty is claimed!"})



        # Track streak
        if killer_id not in self.kill_streak:
            self.kill_streak[killer_id] = 1
        else:
            self.kill_streak[killer_id] += 1

        streak = self.kill_streak[killer_id]

        # Epic Kill
        if streak >= 3:
            self.excitement_level += 20.0
            if killer_obj:
                killer_obj.audience_favor = min(100.0, getattr(killer_obj, "audience_favor", 0.0) + 20.0)
            if hasattr(self.world, 'add_event'):
                # Unique ball type chants
                chant_msg = f"The crowd goes wild for Ball {killer_id}'s {streak}-kill streak!"
                killer_obj = next((b for b in balls if getattr(b, "id", -1) == killer_id), None)
                if killer_obj:
                    k_type = getattr(killer_obj, "ball_type", "").capitalize()
                    if k_type and k_type != "Spectator":
                        chant_msg = f"{k_type}! {k_type}! " + chant_msg

                    self.world.add_event("spawn_booster", {
                        "x": getattr(killer_obj, "x", 0),
                        "y": getattr(killer_obj, "y", 0),
                        "kind": "speed",
                        "value": 30.0
                    })
                self.world.add_event("crowd_cheer", {"message": chant_msg, "volume": 1.0 + (streak * 0.1)})
                self.world.add_event("audio_event", {"sound": "epic_crowd_roar", "volume": 1.0})

        # Team Wipe / Comeback (checking team populations)
        alive_teams = {}
        for b in balls:
            if getattr(b, "alive", False) and getattr(b, "ball_type", "") != "spectator":
                team = getattr(b, "team", getattr(b, "ball_type", ""))
                alive_teams[team] = alive_teams.get(team, 0) + 1

        # Comeback detection: killer's team is heavily outnumbered
        killer = next((b for b in balls if getattr(b, "id", -1) == killer_id), None)
        if killer:
            killer_team = getattr(killer, "team", getattr(killer, "ball_type", ""))
            killer_team_count = alive_teams.get(killer_team, 0)
            total_enemies = sum(count for t, count in alive_teams.items() if t != killer_team)

            if killer_team_count > 0 and total_enemies >= killer_team_count * 3:
                self.excitement_level += 30.0
                killer.audience_favor = min(100.0, getattr(killer, "audience_favor", 0.0) + 30.0)
                if hasattr(self.world, 'add_event'):
                    self.world.add_event("crowd_cheer", {"message": "The crowd roars for an incredible comeback attempt!", "volume": 1.2})
                    self.world.add_event("audio_event", {"sound": "comeback_cheer", "volume": 1.0})

        # Team Wipe detection
        victim = next((b for b in balls if getattr(b, "id", -1) == victim_id), None)
        if victim:
            victim_team = getattr(victim, "team", getattr(victim, "ball_type", ""))
            if alive_teams.get(victim_team, 0) == 0:
                self.excitement_level += 25.0
                if hasattr(self.world, 'add_event'):
                    self.world.add_event("crowd_cheer", {"message": f"The crowd gasps as team {victim_team} is wiped out!", "volume": 1.1})
                    self.world.add_event("audio_event", {"sound": "team_wipe_gasp", "volume": 1.0})


    def _throw_buffs_if_needed(self, balls: List[Any], tick: int):
        if self.excitement_level < 50.0:
            return

        # 1% chance per tick if excitement is high
        if random.random() < 0.01:
            # Find a losing ball to help
            alive_balls = [b for b in balls if getattr(b, "alive", False) and getattr(b, "ball_type", "") != "spectator"]
            if not alive_balls:
                return

            # Find ball with lowest HP percentage
            losing_ball = min(alive_balls, key=lambda b: getattr(b, "hp", 100) / max(1, getattr(b, "max_hp", 100)))

            if hasattr(self.world, 'add_event'):
                self.world.add_event("spawn_booster", {
                    "x": getattr(losing_ball, "x", 0),
                    "y": getattr(losing_ball, "y", 0),
                    "kind": "speed",
                    "value": 30.0
                })
                self.world.add_event("crowd_throw", {"message": "The crowd throws a speed pad to help a struggling player!"})
                self.excitement_level -= 10.0  # Consumes excitement

    def _throw_hazards_if_bored(self, balls: List[Any], tick: int):
        if self.excitement_level >= 20.0:
            return

        if random.random() < 0.01:
            alive_balls = [b for b in balls if getattr(b, "alive", False) and getattr(b, "ball_type", "") != "spectator"]
            if not alive_balls:
                return

            target_ball = random.choice(alive_balls)
            hazard_kind = random.choice(["temporary_wall", "slow_field", "mini_bomb"])

            if hasattr(self.world, 'add_event'):
                self.world.add_event("spawn_hazard", {
                    "x": getattr(target_ball, "x", 0) + random.uniform(-50, 50),
                    "y": getattr(target_ball, "y", 0) + random.uniform(-50, 50),
                    "kind": hazard_kind
                })
                self.world.add_event("crowd_throw", {"message": "The crowd boos and throws a hazard into the arena!"})
                self.excitement_level += 5.0

    def _process_votes(self, balls: List[Any], tick: int):
        if self.vote_cooldown > 0:
            self.vote_cooldown -= 1

        if self.active_vote is None:
            # 1 in 1000 chance per tick to start a vote if excitement is decent
            if self.vote_cooldown == 0 and self.excitement_level >= 30.0 and random.random() < 0.001:
                self._start_vote(balls)
            return

        # Handle active vote
        self.vote_timer -= 1

        # Simulate spectators casting votes
        if not self.has_real_spectators:
            if random.random() < 0.05:  # Random spectator votes
                self._simulate_spectator_vote()

        if self.vote_timer <= 0:
            self._resolve_vote(balls)

    def _process_spectator_signs(self, balls: List[Any], tick: int):
        # Trigger dynamically: 1 in 100 chance per tick if excitement is moderate
        if self.excitement_level < 10.0 or random.random() > 0.01:
            return

        alive_balls = [b for b in balls if getattr(b, "alive", False) and getattr(b, "ball_type", "") != "spectator"]
        if not alive_balls:
            return

        # Pick a random alive ball, heavily weighting those with more kills or hp
        target = random.choice(alive_balls)
        kills = getattr(target, "kills", 0)

        b_type = getattr(target, "ball_type", "Player").capitalize()
        b_id = getattr(target, "id", "?")

        # Determine sign text and size based on kills/performance
        if kills >= 3:
            text = f"UNSTOPPABLE {b_type}-{b_id}!"
            size = 1.5 + (kills * 0.1)
        elif kills > 0:
            text = f"GO {b_type}-{b_id}!"
            size = 1.2 + (kills * 0.1)
        else:
            text = f"We believe in {b_type}-{b_id}!"
            size = 1.0

        if hasattr(self.world, 'add_event'):
            # Calculate position near the edge of the arena or safe zone
            angle = random.uniform(0, 2 * 3.14159)
            radius = 1000.0  # Default fallback
            if hasattr(self.world, 'arena') and hasattr(self.world.arena, 'safe_zone_radius'):
                radius = self.world.arena.safe_zone_radius + 100.0

            import math
            sx = getattr(target, "x", 0) + math.cos(angle) * radius
            sy = getattr(target, "y", 0) + math.sin(angle) * radius

            self.world.add_event("spectator_sign", {
                "x": sx,
                "y": sy,
                "text": text,
                "size": size,
                "duration": 100
            })

    def _start_vote(self, balls: List[Any]):
        vote_types = [
            {"type": "spawn_hazard", "options": ["lava_pit", "spike_trap", "poison_cloud"]},
            {"type": "player_buff", "options": ["speed", "damage", "shield"]},
            {"type": "global_stat_modifier", "options": ["global_speed_up", "global_damage_up", "global_shield_up"]}
        ]
        chosen_vote = random.choice(vote_types)

        self.active_vote = {
            "type": chosen_vote["type"],
            "options": chosen_vote["options"]
        }
        self.votes = {opt: 0 for opt in chosen_vote["options"]}
        self.vote_timer = 200  # Lasts 200 ticks

        if hasattr(self.world, 'add_event'):
            self.world.add_event("vote_started", {
                "message": f"A crowd vote has started for: {chosen_vote['type']}! Options: {', '.join(chosen_vote['options'])}"
            })
            self.world.add_event("audio_event", {"sound": "vote_start_chime", "volume": 1.0})

    def _simulate_spectator_vote(self):
        if not self.active_vote or not self.votes:
            return

        # Pick a random option to vote for
        options = list(self.votes.keys())
        chosen = random.choice(options)
        self.votes[chosen] += 1

    def _resolve_vote(self, balls: List[Any]):
        if not self.active_vote or not self.votes:
            self.active_vote = None
            self.votes = {}
            self.user_votes = {}
            return

        # Find winner
        winner = max(self.votes.items(), key=lambda x: x[1])
        winning_option = winner[0]
        vote_type = self.active_vote["type"]

        if hasattr(self.world, 'add_event'):
            self.world.add_event("vote_ended", {
                "message": f"The crowd has spoken! The winner is {winning_option} with {winner[1]} votes!"
            })
            self.world.add_event("audio_event", {"sound": "vote_end_cheer", "volume": 1.0})

        # Apply the result
        alive_balls = [b for b in balls if getattr(b, "alive", False) and getattr(b, "ball_type", "") != "spectator"]

        if alive_balls:
            if vote_type == "spawn_hazard":
                target = random.choice(alive_balls)
                if hasattr(self.world, 'add_event'):
                    self.world.add_event("spawn_hazard", {
                        "x": getattr(target, "x", 0),
                        "y": getattr(target, "y", 0),
                        "kind": winning_option
                    })
            elif vote_type == "player_buff":
                # Give buff to a random player (or lowest hp)
                target = random.choice(alive_balls)
                if hasattr(self.world, 'add_event'):
                    self.world.add_event("spawn_booster", {
                        "x": getattr(target, "x", 0),
                        "y": getattr(target, "y", 0),
                        "kind": winning_option,
                        "value": 50.0
                    })
            elif vote_type == "global_stat_modifier":
                self.active_global_modifier = winning_option
                self.global_modifier_timer = 1800  # 30 seconds at 60 ticks/sec
                if hasattr(self.world, 'add_event'):
                    self.world.add_event("crowd_cheer", {"message": f"The crowd activated a {winning_option} for 30 seconds!", "volume": 1.2})

        for u, v in getattr(self, 'user_votes', {}).items():
            if v == winning_option:
                self._add_viewer_loyalty(u, 10)
        self.user_votes = {}

        self.active_vote = None
        self.votes = {}
        self.vote_cooldown = 1000  # Long cooldown before next vote


    def _process_audience_favor(self, balls: List[Any], tick: int):
        for b in balls:
            if not getattr(b, "alive", False) or getattr(b, "ball_type", "") == "spectator":
                continue

            favor = getattr(b, "audience_favor", 0.0)

            # Decay favor towards 0
            if favor > 0:
                b.audience_favor = max(0.0, favor - 0.05)
            elif favor < 0:
                b.audience_favor = min(0.0, favor + 0.05)

            favor = getattr(b, "audience_favor", 0.0)

            if favor >= 50.0:
                # Passive healing or cooldown reduction
                if random.random() < 0.05:
                    if getattr(b, "hp", 100) < getattr(b, "max_hp", 100):
                        b.hp = min(getattr(b, "hp", 100) + 1.0, getattr(b, "max_hp", 100))

                    if getattr(b, "attack_timer", 0.0) > 0:
                        b.attack_timer = max(0.0, b.attack_timer - 0.1)
                    if getattr(b, "skill_timer", 0.0) > 0:
                        b.skill_timer = max(0.0, b.skill_timer - 0.1)

            elif favor <= -50.0:
                # Occasionally throw hazards
                if random.random() < 0.005:
                    hazard_kind = random.choice(["temporary_wall", "slow_field", "mini_bomb"])
                    if hasattr(self.world, 'add_event'):
                        self.world.add_event("spawn_hazard", {
                            "x": getattr(b, "x", 0) + random.uniform(-30, 30),
                            "y": getattr(b, "y", 0) + random.uniform(-30, 30),
                            "kind": hazard_kind
                        })
                        self.world.add_event("crowd_throw", {"message": f"The crowd hates Ball {getattr(b, 'id', '?')} and throws a hazard!"})

    def _process_global_modifier(self, balls: List[Any], tick: int):
        if self.global_modifier_timer > 0:
            self.global_modifier_timer -= 1
            if self.global_modifier_timer <= 0:
                self.active_global_modifier = None
                if hasattr(self.world, 'add_event'):
                    self.world.add_event("crowd_cheer", {"message": "The global stat modifier has worn off!", "volume": 1.0})

                for b in balls:
                    if getattr(b, "crowd_global_speed", False):
                        delattr(b, "crowd_global_speed")
                        b.speed = getattr(b, "base_speed", getattr(b, "speed", 100.0))
                    if getattr(b, "crowd_global_damage", False):
                        delattr(b, "crowd_global_damage")
                        b.damage = getattr(b, "base_damage", getattr(b, "damage", 10.0))
                    if getattr(b, "crowd_global_shield", False):
                        delattr(b, "crowd_global_shield")
            else:
                for b in balls:
                    if not getattr(b, "alive", False) or getattr(b, "ball_type", "") == "spectator":
                        continue

                    if self.active_global_modifier == "global_speed_up":
                        b.speed = getattr(b, "base_speed", getattr(b, "speed", 100.0)) * 1.2
                        b.crowd_global_speed = True
                    elif self.active_global_modifier == "global_damage_up":
                        b.damage = getattr(b, "base_damage", getattr(b, "damage", 10.0)) * 1.2
                        b.crowd_global_damage = True
                    elif self.active_global_modifier == "global_shield_up":
                        b.shield = getattr(b, "shield", 0.0) + 0.1  # Passive shield regen
                        if b.shield > 50.0:
                            b.shield = 50.0
                        b.crowd_global_shield = True
