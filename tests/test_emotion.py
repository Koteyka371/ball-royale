import sys
import os

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

def test_contagious_fear():
    import random
    random.seed(42) # Ensure predictable randomness if we want, or just force it

    ball = MockBall(hp=100, max_hp=100)
    world = MockWorld()
    emotion = Emotion(ball, world)

    class FleeingAlly:
        def __init__(self):
            self.current_action = "flee"
            self.hp = 100
            self.max_hp = 100

    ally = FleeingAlly()

    # We force the chance to hit by mocking random
    orig_random = random.random
    random.random = lambda: 0.05

    state = emotion.get_state({"allies": [ally]})

    random.random = orig_random

    assert state == "fear"
    assert emotion.infected_emotion == "fear"
    assert emotion.infection_ticks == 60

def test_contagious_rage():
    import random

    ball = MockBall(hp=100, max_hp=100)
    world = MockWorld()
    emotion = Emotion(ball, world)

    class AggroAlly:
        def __init__(self):
            self.current_action = "attack"
            self.hp = 100
            self.max_hp = 100

    ally = AggroAlly()

    orig_random = random.random
    random.random = lambda: 0.05

    state = emotion.get_state({"allies": [ally]})

    random.random = orig_random

    assert state == "rage"
    assert emotion.infected_emotion == "rage"
    assert emotion.infection_ticks == 60

def test_contagion_decay():
    import random

    ball = MockBall(hp=100, max_hp=100)
    world = MockWorld()
    emotion = Emotion(ball, world)

    class FleeingAlly:
        def __init__(self):
            self.current_action = "flee"
            self.hp = 100
            self.max_hp = 100

    ally = FleeingAlly()

    orig_random = random.random
    random.random = lambda: 0.05

    emotion.get_state({"allies": [ally]})
    assert emotion.infection_ticks == 60

    random.random = lambda: 0.99 # no more infections

    # tick down
    emotion.get_state({"allies": [ally]})
    assert emotion.infection_ticks == 59

    emotion.infection_ticks = 1
    emotion.get_state({})
    assert emotion.infection_ticks == 0
    assert emotion.infected_emotion == "fear"

    emotion.get_state({})
    assert emotion.infected_emotion is None

    random.random = orig_random
