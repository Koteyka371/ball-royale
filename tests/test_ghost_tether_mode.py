import pytest
from ai.game_modes import GAME_MODES

class DummyWorld:
    def __init__(self):
        self.events = []
    def add_event(self, name, data):
        self.events.append((name, data))

class DummyBall:
    def __init__(self, id_val, x=0, y=0):
        self.id = id_val
        self.x = x
        self.y = y
        self.alive = True
        self.is_ghost = False
        self.hp = 100.0
        self.max_hp = 100.0
        self.damage = 10.0
        self.base_damage = 10.0

def test_ghost_tether_turn_ghost():
    mode = GAME_MODES["ghost_tether"]
    world = DummyWorld()
    killer = DummyBall(1, 0, 0)
    victim = DummyBall(2, 50, 50)

    # Simulate death
    mode.on_ball_died(world, victim, killer)

    assert victim.alive == True
    assert victim.is_ghost == True
    assert victim.tether_killer_id == killer.id
    assert victim.hp == 50.0
    assert victim.damage == 5.0
    assert any(e[0] == "ball_turned_ghost" for e in world.events)

def test_ghost_tether_pull():
    mode = GAME_MODES["ghost_tether"]
    world = DummyWorld()
    killer = DummyBall(1, 0, 0)
    victim = DummyBall(2, 400, 0)
    victim.alive = True
    victim.is_ghost = True
    victim.tether_killer_id = killer.id

    balls = [killer, victim]
    mode.tick(world, balls, 1.0)

    # 400 distance > 300 tether range, should pull at 150 speed
    assert victim.x < 400

def test_ghost_tether_revive_on_killer_death():
    mode = GAME_MODES["ghost_tether"]
    world = DummyWorld()
    killer = DummyBall(1, 0, 0)
    killer.alive = False # Killer is dead

    victim = DummyBall(2, 50, 50)
    victim.alive = True
    victim.is_ghost = True
    victim.tether_killer_id = killer.id
    victim.hp = 10.0

    balls = [killer, victim]
    mode.tick(world, balls, 0.1)

    assert victim.is_ghost == False
    assert victim.hp == 100.0
    assert any(e[0] == "ghost_revived" and e[1]["reason"] == "killer_died" for e in world.events)

def test_ghost_tether_revive_on_damage():
    mode = GAME_MODES["ghost_tether"]
    world = DummyWorld()
    killer = DummyBall(1, 0, 0)

    victim = DummyBall(2, 50, 50)
    victim.alive = True
    victim.is_ghost = True
    victim.tether_killer_id = killer.id
    victim.hp = 10.0
    victim.ghost_damage_dealt = 60.0 # Above 50 threshold

    balls = [killer, victim]
    mode.tick(world, balls, 0.1)

    assert victim.is_ghost == False
    assert victim.hp == 100.0
    assert victim.ghost_damage_dealt == 0.0
    assert any(e[0] == "ghost_revived" and e[1]["reason"] == "damage_threshold" for e in world.events)

def test_ghost_tether_revive_on_assist():
    mode = GAME_MODES["ghost_tether"]
    world = DummyWorld()
    killer = DummyBall(1, 0, 0)

    victim = DummyBall(2, 50, 50)
    victim.alive = True
    victim.is_ghost = True
    victim.tether_killer_id = killer.id
    victim.hp = 10.0

    world.balls = [killer, victim]

    another_victim = DummyBall(3, 100, 100)

    # Killer kills someone else, assisting ghost should revive
    mode.on_ball_died(world, another_victim, killer)

    assert victim.is_ghost == False
    assert victim.hp == 100.0
    assert any(e[0] == "ghost_revived" and e[1]["reason"] == "assist" for e in world.events)
