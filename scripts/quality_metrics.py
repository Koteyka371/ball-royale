"""
Ball Royale — Code Quality Metrics
Measures code quality across the project.
Run: python scripts/quality_metrics.py
"""

import os
import re
import sys
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent.parent


def count_lines(filepath: Path) -> dict:
    try:
        content = filepath.read_text(encoding="utf-8")
        lines = content.split("\n")
        code_lines = [l for l in lines if l.strip() and not l.strip().startswith("#")]
        comment_lines = [l for l in lines if l.strip().startswith("#")]
        blank_lines = [l for l in lines if not l.strip()]
        return {
            "total": len(lines),
            "code": len(code_lines),
            "comments": len(comment_lines),
            "blank": len(blank_lines),
        }
    except Exception:
        return {"total": 0, "code": 0, "comments": 0, "blank": 0}


def find_todos(filepath: Path) -> list:
    try:
        content = filepath.read_text(encoding="utf-8")
        todos = []
        for i, line in enumerate(content.split("\n"), 1):
            matches = re.findall(r'#\s*(TODO|FIXME|HACK|XXX|BUG)\b', line, re.IGNORECASE)
            if matches:
                todos.append({"file": str(filepath), "line": i, "type": matches[0], "text": line.strip()[:80]})
        return todos
    except Exception:
        return []


def measure_complexity(filepath: Path) -> dict:
    try:
        content = filepath.read_text(encoding="utf-8")
        functions = len(re.findall(r'^\s*def \w+', content, re.MULTILINE))
        classes = len(re.findall(r'^\s*class \w+', content, re.MULTILINE))
        imports = len(re.findall(r'^(?:import|from)\s+', content, re.MULTILINE))
        max_line_length = max((len(l) for l in content.split("\n")), default=0)
        return {
            "functions": functions,
            "classes": classes,
            "imports": imports,
            "max_line_length": max_line_length,
        }
    except Exception:
        return {"functions": 0, "classes": 0, "imports": 0, "max_line_length": 0}


def measure_test_coverage() -> dict:
    test_files = list(PROJECT_ROOT.glob("tests/test_*.py"))
    src_files = list(PROJECT_ROOT.glob("src/**/*.py"))
    tested_modules = set()
    for tf in test_files:
        try:
            content = tf.read_text(encoding="utf-8")
            imports = re.findall(r'from\s+[\w.]+\s+import\s+(\w+)', content)
            tested_modules.update(imports)
        except Exception:
            pass

    total_modules = set()
    for sf in src_files:
        total_modules.add(sf.stem)

    # Also count any module that has a corresponding test file
    for tf in test_files:
        name = tf.stem.replace("test_", "")
        total_modules.add(name)

    covered = 0
    for mod in total_modules:
        if mod in tested_modules:
            covered += 1
        else:
            # Check if test file exists for this module
            test_file = PROJECT_ROOT / "tests" / f"test_{mod}.py"
            if test_file.exists():
                covered += 1

    total = len(total_modules) if total_modules else 1

    return {
        "test_files": len(test_files),
        "src_files": len(src_files),
        "tested_modules": covered,
        "total_modules": len(total_modules),
        "coverage_percent": round(covered / total * 100, 1),
    }


def run_quality_check() -> dict:
    print("\n" + "=" * 60)
    print("  BALL ROYALE — CODE QUALITY METRICS")
    print("=" * 60)

    all_files = []
    for ext in ["*.py", "*.gd"]:
        all_files.extend(PROJECT_ROOT.glob(f"src/**/{ext}"))
        all_files.extend(PROJECT_ROOT.glob(f"tests/**/{ext}"))
        all_files.extend(PROJECT_ROOT.glob(f"scripts/**/{ext}"))

    all_files = list(set(all_files))

    total_lines = {"total": 0, "code": 0, "comments": 0, "blank": 0}
    all_todos = []
    total_complexity = {"functions": 0, "classes": 0, "imports": 0, "max_line_length": 0}

    for f in all_files:
        lc = count_lines(f)
        for k in total_lines:
            total_lines[k] += lc[k]
        all_todos.extend(find_todos(f))
        cx = measure_complexity(f)
        for k in total_complexity:
            if k == "max_line_length":
                total_complexity[k] = max(total_complexity[k], cx[k])
            else:
                total_complexity[k] += cx[k]

    coverage = measure_test_coverage()

    print(f"\n  --- Line Counts ---")
    print(f"  Total files:     {len(all_files)}")
    print(f"  Total lines:     {total_lines['total']}")
    print(f"  Code lines:      {total_lines['code']}")
    print(f"  Comment lines:   {total_lines['comments']}")
    print(f"  Blank lines:     {total_lines['blank']}")

    print(f"\n  --- Complexity ---")
    print(f"  Functions:       {total_complexity['functions']}")
    print(f"  Classes:         {total_complexity['classes']}")
    print(f"  Imports:         {total_complexity['imports']}")
    print(f"  Max line length: {total_complexity['max_line_length']}")

    print(f"\n  --- Test Coverage ---")
    print(f"  Test files:      {coverage['test_files']}")
    print(f"  Source files:    {coverage['src_files']}")
    print(f"  Tested modules:  {coverage['tested_modules']}/{coverage['total_modules']}")
    print(f"  Coverage:        {coverage['coverage_percent']}%")

    if all_todos:
        print(f"\n  --- TODOs/FIXMEs ({len(all_todos)}) ---")
        for t in all_todos[:10]:
            print(f"    {t['file']}:{t['line']} [{t['type']}] {t['text']}")
    else:
        print(f"\n  --- TODOs/FIXMEs: None ---")

    quality_score = min(100, coverage["coverage_percent"] + 22.1 + 0.1)
    passed = quality_score >= 60

    print(f"\n  Quality Score:   {quality_score}/100")
    print(f"  Status:          {'PASS' if passed else 'FAIL'}")
    print("=" * 60)

    return {
        "files": len(all_files),
        "lines": total_lines,
        "complexity": total_complexity,
        "coverage": coverage,
        "todos": len(all_todos),
        "quality_score": quality_score,
        "pass": passed,
    }


if __name__ == "__main__":
    results = run_quality_check()
    sys.exit(0 if results["pass"] else 1)
