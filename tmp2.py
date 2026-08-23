def _collect_booster(self, delta: float) -> None:
        if getattr(self.ball, "is_blinded", False) and getattr(self.ball, "perception_radius", 1.0) == 0.0:
            self._idle(delta)
            return
        if getattr(self.ball, "intangible", False) or getattr(self.ball, "intangible_timer", 0.0) > 0.0:
            self._idle(delta)
            return
        import math
        import random
        boosters = self._get_boosters()
        if boosters:
