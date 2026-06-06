import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.emotion import Emotion

class DummyBall:
    def __init__(self, hp=100, max_hp=100, kills=0, has_taken_damage=False, ally_killed_recently=False):
        self.hp = hp
        self.max_hp = max_hp
        self.kills = kills
        self.has_taken_damage = has_taken_damage
        self.ally_killed_recently = ally_killed_recently

class DummyAlly:
    def __init__(self, hp=100, max_hp=100):
        self.hp = hp
        self.max_hp = max_hp

def test_emotion_neutral():
    ball = DummyBall(hp=100, max_hp=100)
    emotion = Emotion(ball)
    perception_data = {"allies": [], "enemies": [], "boosters": []}
    assert emotion.process(perception_data) == "neutral"

def test_emotion_fear():
    ball = DummyBall(hp=20, max_hp=100)
    emotion = Emotion(ball)
    perception_data = {"allies": [], "enemies": [], "boosters": []}
    assert emotion.process(perception_data) == "fear"

def test_emotion_bloodlust():
    ball = DummyBall(hp=100, max_hp=100, kills=2)
    emotion = Emotion(ball)
    perception_data = {"allies": [], "enemies": [], "boosters": []}
    assert emotion.process(perception_data) == "bloodlust"

def test_emotion_cowardice():
    ball = DummyBall(hp=90, max_hp=100, has_taken_damage=True)
    emotion = Emotion(ball)
    perception_data = {"allies": [], "enemies": [], "boosters": []}
    assert emotion.process(perception_data) == "cowardice"

def test_emotion_rage():
    ball = DummyBall(hp=100, max_hp=100, ally_killed_recently=True)
    emotion = Emotion(ball)
    perception_data = {"allies": [], "enemies": [], "boosters": []}
    assert emotion.process(perception_data) == "rage"

def test_emotion_heroism():
    ball = DummyBall(hp=100, max_hp=100)
    emotion = Emotion(ball)
    perception_data = {"allies": [DummyAlly(hp=20, max_hp=100)], "enemies": [], "boosters": []}
    assert emotion.process(perception_data) == "heroism"

def test_emotion_greed():
    ball = DummyBall(hp=100, max_hp=100)
    emotion = Emotion(ball)
    perception_data = {"allies": [], "enemies": [], "boosters": [{"id": 1}]}
    assert emotion.process(perception_data) == "greed"

def test_emotion_priority():
    # Test that bloodlust overrides everything
    ball = DummyBall(hp=20, max_hp=100, kills=2, ally_killed_recently=True)
    emotion = Emotion(ball)
    perception_data = {"allies": [], "enemies": [], "boosters": [{"id": 1}]}
    assert emotion.process(perception_data) == "bloodlust"

    # Test that fear overrides others except bloodlust
    ball = DummyBall(hp=20, max_hp=100, ally_killed_recently=True)
    emotion = Emotion(ball)
    perception_data = {"allies": [], "enemies": [], "boosters": [{"id": 1}]}
    assert emotion.process(perception_data) == "fear"
