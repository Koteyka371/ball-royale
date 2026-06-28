from typing import Dict, List, Any

class StatsOverlay:
    def __init__(self, max_top_killers: int = 3):
        self.max_top_killers = max_top_killers
        self.stats: Dict[str, Any] = {
            "alive_count": 0,
            "total_kills": 0,
            "top_killers": []
        }

    def update(self, balls: List[Dict[str, Any]]) -> None:
        """
        Expects a list of dictionaries representing balls.
        Each ball should have 'id', 'type', 'hp', 'kills'.
        """
        alive_balls = [b for b in balls if b.get('hp', 0) > 0]
        self.stats["alive_count"] = len(alive_balls)

        total_kills = sum(b.get('kills', 0) for b in balls)
        self.stats["total_kills"] = total_kills

        sorted_balls = sorted(balls, key=lambda b: (-b.get('kills', 0), b.get('id', 0)))
        top_killers: List[Dict[str, Any]] = []
        for b in sorted_balls:
            if b.get('kills', 0) > 0 and len(top_killers) < self.max_top_killers:
                top_killers.append({
                    "id": b.get('id', '?'),
                    "type": str(b.get('type', 'unknown')).upper(),
                    "kills": b.get('kills', 0),
                    "stamina": b.get('stamina', 100.0)
                })
        self.stats["top_killers"] = top_killers

    def get_stats(self) -> Dict[str, Any]:
        return self.stats

    def format_text(self) -> str:
        lines = []
        lines.append(f"Alive: {self.stats['alive_count']}")
        lines.append(f"Total Kills: {self.stats['total_kills']}")
        if self.stats['top_killers']:
            lines.append("Top Killers:")
            for k in self.stats['top_killers']:
                lines.append(f" - {k['type']}-{k['id']}: {k['kills']} kills (Stamina: {int(k.get('stamina', 100))}%)")
        return "\n".join(lines)
