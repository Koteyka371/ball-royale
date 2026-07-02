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

    def tick(self, balls: List[Any], kill_log: List[Dict[str, Any]], tick: int):
        self._update_excitement(tick)
        self._check_events(balls, kill_log, tick)
        self._throw_buffs_if_needed(balls, tick)
        self._throw_hazards_if_bored(balls, tick)

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
                self.world.add_event("crowd_cheer", {"message": f"The crowd goes wild for Ball {killer_id}'s {streak}-kill streak!", "volume": 1.0 + (streak * 0.1)})
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
        from arena.interactive_crowd_hazards import InteractiveCrowdHazards
        self.excitement_level = InteractiveCrowdHazards.process_boredom(self.excitement_level, balls, self.world)
