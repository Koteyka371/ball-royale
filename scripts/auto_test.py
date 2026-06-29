"""Auto-test system that runs all tests and reports results."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any


def run_tests(test_dir: Path = Path("tests")) -> dict[str, Any]:
    """Run all tests and return results."""
    if not test_dir.exists():
        return {
            "status": "no_tests",
            "message": "No tests directory found",
            "passed": 0,
            "failed": 0,
            "skipped": 0
        }
    
    test_files = list(test_dir.glob("**/test_*.py"))
    if not test_files:
        return {
            "status": "no_tests",
            "message": "No test files found",
            "passed": 0,
            "failed": 0,
            "skipped": 0
        }
    
    # Run pytest
    try:
        result = subprocess.run(
            ["pytest", str(test_dir), "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        # Parse output
        output = result.stdout + result.stderr
        
        # Count results
        passed = output.count("PASSED")
        failed = output.count("FAILED")
        skipped = output.count("SKIPPED")
        
        return {
            "status": "success" if result.returncode == 0 else "failed",
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "total": passed + failed + skipped,
            "output": output
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "message": "Tests timed out after 120 seconds",
            "passed": 0,
            "failed": 0,
            "skipped": 0
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "passed": 0,
            "failed": 0,
            "skipped": 0
        }


def run_validation() -> dict[str, Any]:
    """Run task manifest validation."""
    try:
        result = subprocess.run(
            [sys.executable, "scripts/validate_tasks.py", "agent_tasks.json"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return {
            "status": "success" if result.returncode == 0 else "failed",
            "output": result.stdout + result.stderr
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


def check_code_quality() -> dict[str, Any]:
    """Check code quality if tools are available."""
    results = {}
    
    # Check ruff
    try:
        result = subprocess.run(
            ["ruff", "check", "src/", "tests/"],
            capture_output=True,
            text=True,
            timeout=30
        )
        results["ruff"] = {
            "status": "success" if result.returncode == 0 else "issues",
            "output": result.stdout
        }
    except FileNotFoundError:
        results["ruff"] = {"status": "not_installed", "message": "ruff not installed"}
    except Exception as e:
        results["ruff"] = {"status": "error", "message": str(e)}
    
    # Check mypy
    try:
        result = subprocess.run(
            ["mypy", "--explicit-package-bases", "src/", "tests/"],
            env={"MYPYPATH": "src", **__import__("os").environ},
            capture_output=True,
            text=True,
            timeout=30
        )
        results["mypy"] = {
            "status": "success" if result.returncode == 0 else "issues",
            "output": result.stdout
        }
    except FileNotFoundError:
        results["mypy"] = {"status": "not_installed", "message": "mypy not installed"}
    except Exception as e:
        results["mypy"] = {"status": "error", "message": str(e)}
    
    return results


def main():
    """Main entry point."""
    print("=" * 60)
    print("BALL ROYALE - AUTO TEST SYSTEM")
    print("=" * 60)
    
    # Run validation
    print("\n📋 VALIDATING TASK MANIFEST...")
    validation = run_validation()
    if validation["status"] == "success":
        print("  ✅ Validation passed!")
    else:
        print(f"  ❌ Validation failed: {validation.get('output', 'Unknown error')}")
    
    # Run tests
    print("\n🧪 RUNNING TESTS...")
    tests = run_tests()
    print(f"  Status: {tests['status']}")
    print(f"  Passed: {tests['passed']}")
    print(f"  Failed: {tests['failed']}")
    print(f"  Skipped: {tests['skipped']}")
    print(f"  Total: {tests.get('total', 0)}")
    
    if tests["status"] == "failed":
        print("\n  Test output:")
        print("  " + "-" * 50)
        for line in tests.get("output", "").split("\n")[-20:]:
            print(f"  {line}")
        print("  " + "-" * 50)
    
    # Check code quality
    print("\n🔍 CHECKING CODE QUALITY...")
    quality = check_code_quality()
    for tool, result in quality.items():
        if result["status"] == "not_installed":
            print(f"  ⚠️ {tool}: Not installed")
        elif result["status"] == "success":
            print(f"  ✅ {tool}: Passed")
        else:
            print(f"  ❌ {tool}: Issues found")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    all_passed = (
        validation["status"] == "success" and
        tests["status"] in ("success", "no_tests") and
        quality["ruff"]["status"] in ("success", "not_installed")
    )
    
    if all_passed:
        print("✅ All checks passed! Ready to commit.")
    else:
        print("❌ Some checks failed. Fix issues before committing.")
    
    print("\n" + "=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
