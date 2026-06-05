"""Test AI behaviors to ensure they work correctly."""

from __future__ import annotations

import sys
from pathlib import Path


class MockBall:
    """Mock ball for testing AI behaviors."""
    
    def __init__(
        self,
        hp: int = 100,
        max_hp: int = 100,
        attack: int = 10,
        speed: int = 5,
        x: float = 0,
        y: float = 0
    ):
        self.hp = hp
        self.max_hp = max_hp
        self.attack = attack
        self.speed = speed
        self.x = x
        self.y = y
        self.target = None
        self.state = "idle"
    
    def distance_to(self, other: "MockBall") -> float:
        """Calculate distance to another ball."""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
    
    def is_low_hp(self) -> bool:
        """Check if HP is low."""
        return self.hp < self.max_hp * 0.3
    
    def take_damage(self, amount: int) -> None:
        """Take damage."""
        self.hp = max(0, self.hp - amount)


class MockAI:
    """Mock AI for testing."""
    
    def __init__(self, ball: MockBall):
        self.ball = ball
    
    def should_flee(self, enemies: list[MockBall]) -> bool:
        """Determine if ball should flee."""
        if self.ball.is_low_hp():
            return True
        
        nearby_enemies = [
            e for e in enemies
            if self.ball.distance_to(e) < 100
        ]
        
        return len(nearby_enemies) > 2
    
    def should_attack(self, enemies: list[MockBall]) -> bool:
        """Determine if ball should attack."""
        if self.ball.is_low_hp():
            return False
        
        nearby_enemies = [
            e for e in enemies
            if self.ball.distance_to(e) < 50
        ]
        
        return len(nearby_enemies) > 0
    
    def select_target(self, enemies: list[MockBall]) -> MockBall | None:
        """Select best target to attack."""
        if not enemies:
            return None
        
        return min(enemies, key=lambda e: e.hp)
    
    def decide_action(self, enemies: list[MockBall]) -> str:
        """Decide what action to take."""
        if self.should_flee(enemies):
            return "flee"
        elif self.should_attack(enemies):
            target = self.select_target(enemies)
            if target:
                return "attack"
        return "idle"


def test_ball_creation():
    """Test ball creation."""
    ball = MockBall(hp=150, attack=20, speed=4)
    
    assert ball.hp == 150
    assert ball.attack == 20
    assert ball.speed == 4
    assert ball.x == 0
    assert ball.y == 0
    
    print("[OK] Ball creation test passed")


def test_distance_calculation():
    """Test distance calculation."""
    ball1 = MockBall(x=0, y=0)
    ball2 = MockBall(x=3, y=4)
    
    distance = ball1.distance_to(ball2)
    
    assert distance == 5.0
    
    print("[OK] Distance calculation test passed")


def test_low_hp_detection():
    """Test low HP detection."""
    ball = MockBall(hp=25, max_hp=100)
    
    assert ball.is_low_hp() is True
    
    ball.hp = 80
    
    assert ball.is_low_hp() is False
    
    print("[OK] Low HP detection test passed")


def test_flee_decision():
    """Test flee decision."""
    ball = MockBall(hp=25, max_hp=100)
    ai = MockAI(ball)
    enemies = [MockBall(x=10, y=0) for _ in range(3)]
    
    assert ai.should_flee(enemies) is True
    
    ball.hp = 80
    enemies = [MockBall(x=10, y=0)]
    
    assert ai.should_flee(enemies) is False
    
    print("[OK] Flee decision test passed")


def test_attack_decision():
    """Test attack decision."""
    ball = MockBall(hp=80, max_hp=100)
    ai = MockAI(ball)
    enemies = [MockBall(x=10, y=0)]
    
    assert ai.should_attack(enemies) is True
    
    ball.hp = 20
    enemies = [MockBall(x=10, y=0)]
    
    assert ai.should_attack(enemies) is False
    
    print("[OK] Attack decision test passed")


def test_target_selection():
    """Test target selection."""
    ball = MockBall(x=0, y=0)
    ai = MockAI(ball)
    enemies = [
        MockBall(hp=100, x=10, y=0),
        MockBall(hp=50, x=15, y=0),
        MockBall(hp=20, x=20, y=0)
    ]
    
    target = ai.select_target(enemies)
    
    assert target is not None
    assert target.hp == 20
    
    print("[OK] Target selection test passed")


def test_action_decision():
    """Test action decision."""
    ball = MockBall(hp=80, max_hp=100)
    ai = MockAI(ball)
    enemies = [MockBall(x=10, y=0)]
    
    action = ai.decide_action(enemies)
    
    assert action == "attack"
    
    ball.hp = 20
    enemies = [MockBall(x=10, y=0) for _ in range(3)]
    
    action = ai.decide_action(enemies)
    
    assert action == "flee"
    
    print("[OK] Action decision test passed")


def main():
    """Run all tests."""
    print("=" * 60)
    print("BALL ROYALE - AI BEHAVIOR TESTS")
    print("=" * 60)
    
    tests = [
        test_ball_creation,
        test_distance_calculation,
        test_low_hp_detection,
        test_flee_decision,
        test_attack_decision,
        test_target_selection,
        test_action_decision
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"[FAIL] {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"[FAIL] {test.__name__} error: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
