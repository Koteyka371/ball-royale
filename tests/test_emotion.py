import sys
import os

# Add src to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.emotion import Emotion

class MockBall:
    def __init__(self, hp=100, max_hp=100, kills=0, just_hit=False):
        self.hp = hp
        self.max_hp = max_hp
        self.kills = kills
        self.just_hit = just_hit

def test_emotion_fear():
    ball = MockBall(hp=20, max_hp=100) # 20% HP
    emotion_layer = Emotion(ball)
    perception_data = {"enemies": [], "allies": [], "boosters": []}
    assert emotion_layer.process(perception_data) == "fear"

def test_emotion_bloodlust():
    ball = MockBall(hp=50, max_hp=100, kills=2)
    emotion_layer = Emotion(ball)
    perception_data = {"enemies": [], "allies": [], "boosters": []}
    assert emotion_layer.process(perception_data) == "bloodlust"

def test_emotion_heroism():
    ball = MockBall(hp=50, max_hp=100, kills=1)
    emotion_layer = Emotion(ball)
    ally = MockBall(hp=20, max_hp=100)
    perception_data = {"enemies": [], "allies": [ally], "boosters": []}
    assert emotion_layer.process(perception_data) == "heroism"

def test_emotion_greed():
    ball = MockBall(hp=50, max_hp=100, kills=1)
    emotion_layer = Emotion(ball)
    ally = MockBall(hp=100, max_hp=100)
    perception_data = {"enemies": [], "allies": [ally], "boosters": [{"id": "b1"}]}
    assert emotion_layer.process(perception_data) == "greed"

def test_emotion_rage():
    ball = MockBall(hp=90, max_hp=100, kills=1) # 90% HP
    emotion_layer = Emotion(ball)
    perception_data = {"enemies": [{"id": "e1"}], "allies": [], "boosters": []}
    assert emotion_layer.process(perception_data) == "rage"

def test_emotion_cowardice():
    ball = MockBall(hp=90, max_hp=100, kills=1, just_hit=True) # 90% HP
    emotion_layer = Emotion(ball)
    perception_data = {"enemies": [], "allies": [], "boosters": []}
    assert emotion_layer.process(perception_data) == "cowardice"

def test_emotion_neutral():
    ball = MockBall(hp=50, max_hp=100, kills=1) # 50% HP
    emotion_layer = Emotion(ball)
    perception_data = {"enemies": [{"id": "e1"}], "allies": [], "boosters": []}
    assert emotion_layer.process(perception_data) == "neutral"
