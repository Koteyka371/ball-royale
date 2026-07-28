import pytest
from src.ai.action import Action
class MockWorld:
    def __init__(self):
        self.arena = type('A', (), {'hazards': []})()
        self.balls = []
def test_mimic():
    world = MockWorld()
    b = type('B', (), {'id': 1, 'x': 50, 'y': 50, 'alive': True, 'team': 'player'})()
    action = Action(b, world)
