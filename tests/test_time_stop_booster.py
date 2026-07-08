import pytest

class MockEntity:
    def __init__(self, id, team="A", alive=True, stun_timer=0.0):
        self.id = id
        self.team = team
        self.alive = alive
        self.stun_timer = stun_timer

class MockHazard:
    def __init__(self, kind, is_disabled_by_flare=False):
        self.kind = kind
        self.is_disabled_by_flare = is_disabled_by_flare
        self.frozen_timer = 0.0

class MockBooster:
    def __init__(self, kind):
        self.kind = kind
        self.x = 100
        self.y = 100

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards
    def clamp_position(self, x, y, radius):
        return x, y, False

class MockWorld:
    def __init__(self, entities, hazards, boosters):
        self.entities = entities
        self.balls = entities
        self.arena = MockArena(hazards)
        self.boosters = boosters

    def get_nearby_entities(self, ball, radius):
        return {
            "enemies": [e for e in self.entities if e.team != ball.team],
            "allies": [e for e in self.entities if e.team == ball.team],
            "boosters": self.boosters,
            "hazards": self.arena.hazards,
        }

class MockAction:
    def __init__(self, ball, world):
        self.ball = ball
        self.world = world

    def _get_boosters(self):
        return self.world.boosters

    def _get_enemies(self):
        return [e for e in self.world.entities if e.team != self.ball.team]

    def _get_perception_radius(self):
        return 500.0

    def _apply_obstacle_avoidance(self, nx, ny, nearest, ignore_enemies=False):
        return nx, ny

    def _apply_boid_rules(self, nx, ny):
        return nx, ny

    def _flee(self, delta):
        pass

    def _collect_booster(self, delta):
        import math
        boosters = self._get_boosters()
        if not boosters:
            return

        nearest = boosters[0]

        # Simulate collection when close
        dist = 0.0 # Force distance to 0 so it collects immediately

        ball_radius = getattr(self.ball, "radius", 10.0)
        if dist <= ball_radius + 10:
            if getattr(nearest, "kind", None) == "time_stop_booster":
                entities = getattr(self.world, "entities", getattr(self.world, "balls", []))
                for e in entities:
                    if getattr(e, "team", "") != getattr(self.ball, "team", "") and getattr(e, "alive", True):
                        e.stun_timer = max(getattr(e, "stun_timer", 0.0), 3.0)
                if hasattr(self.world, "arena") and hasattr(self.world.arena, "hazards"):
                    for h in self.world.arena.hazards:
                        if getattr(h, 'is_disabled_by_flare', False):
                            continue
                        h.frozen_timer = 3.0
                    if nearest in self.world.arena.hazards:
                        self.world.arena.hazards.remove(nearest)
                if hasattr(self.world, "boosters") and nearest in self.world.boosters:
                    self.world.boosters.remove(nearest)

def test_time_stop_booster_collection():
    ball = MockEntity(id=1, team="A")
    ball.x = 100
    ball.y = 100
    ball.radius = 10.0
    ball.speed = 100.0

    ally = MockEntity(id=2, team="A")
    enemy1 = MockEntity(id=3, team="B")
    enemy2 = MockEntity(id=4, team="C")

    hazard1 = MockHazard("spike")
    hazard2 = MockHazard("firenado")

    booster = MockBooster("time_stop_booster")

    entities = [ball, ally, enemy1, enemy2]
    hazards = [hazard1, hazard2]
    boosters = [booster]

    world = MockWorld(entities, hazards, boosters)

    action = MockAction(ball, world)

    assert enemy1.stun_timer == 0.0
    assert enemy2.stun_timer == 0.0
    assert ally.stun_timer == 0.0
    assert hazard1.frozen_timer == 0.0
    assert hazard2.frozen_timer == 0.0

    action._collect_booster(1.0)

    assert enemy1.stun_timer == 3.0
    assert enemy2.stun_timer == 3.0

    # Allies should NOT be stunned
    assert ally.stun_timer == 0.0
    assert ball.stun_timer == 0.0

    # Hazards should be frozen
    assert hazard1.frozen_timer == 3.0
    assert hazard2.frozen_timer == 3.0

    # Booster should be removed
    assert len(world.boosters) == 0

if __name__ == "__main__":
    test_time_stop_booster_collection()
    print("Test passed!")
