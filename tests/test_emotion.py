import sys
import os
import pytest

# Add src to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.emotion import Emotion

class MockBall:
    def __init__(self, hp=100, max_hp=100, first_hit_taken=False, kills=0):
        self.hp = hp
        self.max_hp = max_hp
        self.first_hit_taken = first_hit_taken
        self.kills = kills

    def get_hp_percent(self):
        return self.hp / self.max_hp if self.max_hp > 0 else 0.0

class MockWorld:
    def __init__(self):
        pass

def test_neutral():
    ball = MockBall(hp=100, max_hp=100)
    world = MockWorld()
    emotion = Emotion(ball, world)

    # 100% HP, no enemies, no allies in danger, no boosters, no first hit, no kills
    state = emotion.get_state({})
    assert state == "neutral"

def test_fear():
    ball = MockBall(hp=20, max_hp=100)
    world = MockWorld()
    emotion = Emotion(ball, world)

    # HP < 30% triggers fear, even if there are boosters (fear overrides greed)
    state = emotion.get_state({"boosters": [1]})
    assert state == "fear"

def test_cowardice():
    ball = MockBall(hp=80, max_hp=100, first_hit_taken=True)
    world = MockWorld()
    emotion = Emotion(ball, world)

    # first_hit_taken should trigger cowardice
    state = emotion.get_state({})
    assert state == "cowardice"

    # Should only trigger once
    state2 = emotion.get_state({})
    assert state2 == "neutral"

def test_heroism():
    ball = MockBall(hp=100, max_hp=100)
    world = MockWorld()
    emotion = Emotion(ball, world)

    # ally with < 30% HP triggers heroism
    ally = MockBall(hp=10, max_hp=100)
    state = emotion.get_state({"allies": [ally]})
    assert state == "heroism"

def test_bloodlust():
    ball = MockBall(hp=100, max_hp=100, kills=2)
    world = MockWorld()
    emotion = Emotion(ball, world)

    # >= 2 kills triggers bloodlust
    state = emotion.get_state({})
    assert state == "bloodlust"

def test_greed():
    ball = MockBall(hp=100, max_hp=100)
    world = MockWorld()
    emotion = Emotion(ball, world)

    # seeing boosters triggers greed
    state = emotion.get_state({"boosters": [1, 2]})
    assert state == "greed"

def test_rage():
    ball = MockBall(hp=100, max_hp=100)
    world = MockWorld()
    emotion = Emotion(ball, world)

    # HP > 80% and seeing enemies triggers rage
    state = emotion.get_state({"enemies": [1]})
    assert state == "rage"

def test_priority():
    ball = MockBall(hp=20, max_hp=100, first_hit_taken=True, kills=5)
    world = MockWorld()
    emotion = Emotion(ball, world)
    ally = MockBall(hp=10, max_hp=100)

    perception = {
        "allies": [ally],
        "boosters": [1],
        "enemies": [1]
    }

    # Fear (HP < 30%) should override everything else
    state = emotion.get_state(perception)
    assert state == "fear"
