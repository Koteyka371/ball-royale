from typing import List, Dict, Any, Optional

class CameraSystem:
    def __init__(self, width: int = 800, height: int = 600):
        self.width = width
        self.height = height
        self.x = width / 2
        self.y = height / 2
        self.zoom = 1.0
        self.target_id: Optional[int] = None
        self.activity_scores: Dict[int, float] = {}
        self.smoothing = 0.1
        self.shake_intensity = 0.0

    def update(self, balls: List[Dict[str, Any]], events: List[Dict[str, Any]]):
        # Calculate activity score for each ball
        # Factors: recent kills, taking damage, using skills, low HP survival

        # Decay previous scores
        for b_id in self.activity_scores:
            self.activity_scores[b_id] *= 0.9

        for ball in balls:
            b_id_raw = ball.get("id")
            b_id_val = int(b_id_raw) if b_id_raw is not None else None
            if b_id_val is None:
                continue

            if b_id_val not in self.activity_scores:
                self.activity_scores[b_id_val] = 0.0

            hp = ball.get("hp", 0)
            max_hp = ball.get("max_hp", 100)

            if hp <= 0:
                self.activity_scores[b_id_val] = 0.0
                continue

            # Base score for being alive
            score_increase = 0.1

            # Bonus for being low HP (clutch moments)
            if hp / max_hp < 0.2:
                score_increase += 2.0

            self.activity_scores[b_id_val] += score_increase

        # Add score from events
        for event in events:
            if event.get("type") == "kill":
                killer_id = event.get("killer_id")
                if killer_id is not None and killer_id in self.activity_scores:
                    self.activity_scores[killer_id] += 50.0
            elif event.get("type") == "damage":
                victim_id = event.get("victim_id")
                attacker_id = event.get("attacker_id")
                if victim_id is not None and victim_id in self.activity_scores:
                    self.activity_scores[victim_id] += 5.0
                if attacker_id is not None and attacker_id in self.activity_scores:
                    self.activity_scores[attacker_id] += 5.0
            elif event.get("type") == "skill":
                actor_id = event.get("ball_id")
                if actor_id is not None and actor_id in self.activity_scores:
                    self.activity_scores[actor_id] += 10.0
            elif event.get("type") == "earthquake":
                intensity = event.get("intensity", 1.0)
                self.shake_intensity += intensity * 50.0

        # Decay shake intensity
        self.shake_intensity = max(0.0, self.shake_intensity - 2.0)

        # Find most active ball
        best_score = -1.0
        best_id = None
        for ball in balls:
            b_id_raw = ball.get("id")
            b_id_val = int(b_id_raw) if b_id_raw is not None else None
            if b_id_val is not None and ball.get("hp", 0) > 0:
                score = self.activity_scores.get(b_id_val, 0.0)
                if score > best_score:
                    best_score = score
                    best_id = b_id_val

        if best_id is not None:
            self.target_id = best_id

        # Update position
        if self.target_id is not None:
            target_ball = None
            for ball in balls:
                if ball.get("id") == self.target_id:
                    target_ball = ball
                    break

            if target_ball is not None:
                tx = target_ball.get("x", self.x)
                ty = target_ball.get("y", self.y)

                # Smooth follow
                self.x += (tx - self.x) * self.smoothing
                self.y += (ty - self.y) * self.smoothing

                # Dynamic zoom (zoom in for low HP / high action)
                target_zoom = 1.0 + min(1.0, best_score / 100.0)
                self.zoom += (target_zoom - self.zoom) * self.smoothing

    def get_state(self) -> Dict[str, Any]:
        import random
        ox = random.uniform(-self.shake_intensity, self.shake_intensity) if self.shake_intensity > 0 else 0.0
        oy = random.uniform(-self.shake_intensity, self.shake_intensity) if self.shake_intensity > 0 else 0.0
        return {
            "x": self.x + ox,
            "y": self.y + oy,
            "zoom": self.zoom,
            "target_id": self.target_id
        }
