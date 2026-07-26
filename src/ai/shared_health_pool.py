from ai.game_modes import GameMode

class SharedHealthPoolMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Shared Health Pool"
        self.description = "Teams share a single massive health pool. Taking damage drains from the collective pool. When it reaches 0, the entire team is eliminated simultaneously."
        self.team_health = {}
        self.team_max_health = {}

    def setup(self, world, balls):
        super().setup(world, balls)
        self.team_health = {}
        self.team_max_health = {}

        # Calculate max health per team
        for b in balls:
            if not getattr(b, "alive", False) or getattr(b, "ball_type", "") == "spectator":
                continue
            team = getattr(b, "team", getattr(b, "ball_type", "unknown"))
            if team not in self.team_max_health:
                self.team_max_health[team] = 0.0
                self.team_health[team] = 0.0
            self.team_max_health[team] += getattr(b, "max_hp", 100.0)
            self.team_health[team] += getattr(b, "hp", getattr(b, "max_hp", 100.0))

        for b in balls:
            if not getattr(b, "alive", False) or getattr(b, "ball_type", "") == "spectator":
                continue
            b.max_hp = self.team_max_health[getattr(b, "team", getattr(b, "ball_type", "unknown"))]
            b.hp = self.team_health[getattr(b, "team", getattr(b, "ball_type", "unknown"))]

    def tick(self, world, balls, delta: float = 0.016):
        # Calculate current total health from remaining members
        current_team_health = {}
        for b in balls:
            if not getattr(b, "alive", False) or getattr(b, "ball_type", "") == "spectator":
                continue
            team = getattr(b, "team", getattr(b, "ball_type", "unknown"))
            if team not in current_team_health:
                current_team_health[team] = []
            current_team_health[team].append(b)

        for team, members in current_team_health.items():
            if team not in self.team_health:
                continue

            # Calculate hp deltas for all members
            total_damage = 0.0
            total_healing = 0.0
            for m in members:
                m_hp = getattr(m, "hp", 0.0)
                if m_hp < self.team_health[team]:
                    total_damage += (self.team_health[team] - m_hp)
                elif m_hp > self.team_health[team]:
                    total_healing += (m_hp - self.team_health[team])

            if total_damage > 0:
                self.team_health[team] -= total_damage
            elif total_healing > 0:
                self.team_health[team] += total_healing

            if self.team_health[team] <= 0:
                self.team_health[team] = 0
                for m in members:
                    m.hp = 0
                    m.alive = False
                    if hasattr(world, "add_event"):
                        world.add_event("player_died", {"player_id": getattr(m, "id", None)})
            else:
                for m in members:
                    m.hp = self.team_health[team]
                    m.max_hp = self.team_max_health.get(team, m.max_hp)
