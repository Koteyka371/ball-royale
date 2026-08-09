import pytest
from ai.action import Action
from ai.game_modes import GameMode

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards

class MockWorld:
    def __init__(self, arena, boosters, balls):
        self.arena = arena
        self.boosters = boosters
        self.balls = balls
        self.events = []

    def add_event(self, name, data):
        self.events.append((name, data))

class MockEntity:
    def __init__(self, id, x, y, kind, team="team_a"):
        self.id = id
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = 15.0
        self.active = True
        self.intangible = False
        self.intangible_timer = 0.0
        self.team = team
        self.alive = True
        self.grave_robber_shovel_active = False

def test_grave_robber_shovel_pickup():
    shovel = MockEntity(10, 100, 100, "grave_robber_shovel")
    arena = MockArena([shovel])
    world = MockWorld(arena, [shovel], [])

    ball = MockEntity(1, 100, 100, "player")
    action = Action(ball, world)

    # Mocking _get_boosters to return the shovel
    action._get_boosters = lambda: [shovel]

    # Executing the collection logic
    action._collect_booster(0.1)

    assert getattr(ball, "grave_robber_shovel_active", False), "Player should have shovel active"
    assert not shovel.active, "Shovel should be inactive after collection"
    assert shovel not in world.boosters, "Shovel should be removed from world boosters"
    assert shovel not in world.arena.hazards, "Shovel should be removed from arena hazards"

def test_grave_robber_shovel_neutralizes_trap():
    player = MockEntity(1, 100, 100, "player", team="team_a")
    player.grave_robber_shovel_active = True

    grave_trap = MockEntity(20, 100, 100, "grave_trap", team="team_b")
    grave_trap.radius = 30.0
    grave_trap.owner_team = "team_b"

    arena = MockArena([grave_trap])
    world = MockWorld(arena, [], [player])

    mode = GameMode()
    mode.tick(world, world.balls, 0.1)

    assert not player.grave_robber_shovel_active, "Shovel active state should be consumed"
    assert grave_trap not in world.arena.hazards, "Trap should be removed from arena"

    # Check that a new booster spawned
    new_boosters = [b for b in world.boosters if b.kind in ["health_booster", "stamina_booster", "chameleon_item"]]
    assert len(new_boosters) == 1, "Exactly one new item should drop from the neutralized trap"
    assert new_boosters[0].x == grave_trap.x, "Dropped item should be at the trap's X coordinate"
    assert new_boosters[0].y == grave_trap.y, "Dropped item should be at the trap's Y coordinate"

    # Verify no explosion event, but neutralized event
    explosion_events = [e for e in world.events if e[0] == "grave_trap_explosion"]
    neutralized_events = [e for e in world.events if e[0] == "grave_trap_neutralized"]
    assert len(explosion_events) == 0, "Grave trap should not explode"
    assert len(neutralized_events) == 1, "Grave trap should emit neutralized event"
