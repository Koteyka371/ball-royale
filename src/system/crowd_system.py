from typing import Dict, List, Any
import random

class CrowdSystem:
    def __init__(self, world):
        self.world = world
        self.excitement_level = 0.0
        self.max_excitement = 100.0
        self.team_alive_counts = {}
        self.last_kill_tick = 0
        self.kill_streak = {}
        self.active_vote = None
        self.vote_timer = 0
        self.votes = {}
        self.vote_cooldown = 0
        self.ball_positions = {}
        self.camping_time = {}
        self.underdog_team = None
        self.match_started = False
        self.match_ended = False

    def tick(self, balls: List[Any], kill_log: List[Dict[str, Any]], tick: int):
        self._check_bets_and_winner(balls, tick)
        self._update_excitement(tick)
        self._check_events(balls, kill_log, tick)
        self._check_camping(balls, tick)
        self._throw_buffs_if_needed(balls, tick)
        self._throw_hazards_if_bored(balls, tick)
        self._process_votes(balls, tick)

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

    def _handle_kill(self, kill_info: Dict, tick: int, balls: List[Any]):
        killer_id = kill_info.get("killer_id")
        victim_id = kill_info.get("victim_id")

        # Track streak
        if killer_id not in self.kill_streak:
            self.kill_streak[killer_id] = 1
        else:
            self.kill_streak[killer_id] += 1

        streak = self.kill_streak[killer_id]

        # Epic Kill
        if streak >= 3:
            self.excitement_level += 20.0
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
        if random.random() < 0.05:  # Random spectator votes
            self._simulate_spectator_vote()

        if self.vote_timer <= 0:
            self._resolve_vote(balls)

    def _start_vote(self, balls: List[Any]):
        vote_types = [
            {"type": "spawn_hazard", "options": ["lava_pit", "spike_trap", "poison_cloud"]},
            {"type": "player_buff", "options": ["speed", "damage", "shield"]}
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

        self.active_vote = None
        self.votes = {}
        self.vote_cooldown = 1000  # Long cooldown before next vote
