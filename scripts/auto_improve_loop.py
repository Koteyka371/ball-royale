"""
Auto-Improvement Loop.
Runs quality checks, idea generation, test validation, and automatically creates task entries.
"""
import json
import subprocess
import sys
from pathlib import Path

# Paths
TASK_FILE = Path("agent_tasks.json")
GAME_DESIGN_FILE = Path("docs/game_design.md")

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def task_exists(tasks, title_or_id):
    title_lower = title_or_id.lower()
    for t in tasks:
        if t.get("id", "").lower() == title_lower or t.get("title", "").lower() == title_lower:
            return True
    return False

def add_task(manifest, task_id, title, desc, area, risk="medium", allowed_paths=None, acceptance=None):
    if task_exists(manifest.get("tasks", []), task_id) or task_exists(manifest.get("tasks", []), title):
        return False
    
    if allowed_paths is None:
        allowed_paths = ["src/**", "tests/**"]
    if acceptance is None:
        acceptance = ["Feature implemented successfully", "Tests pass"]

    new_task = {
        "id": task_id,
        "status": "todo",
        "area": area,
        "risk": risk,
        "title": title,
        "description": desc,
        "allowed_paths": allowed_paths,
        "acceptance": acceptance
    }
    manifest.setdefault("tasks", []).append(new_task)
    print(f"[Auto-Improve] Generated task: {task_id} - {title}")
    return True

def main():
    if not TASK_FILE.exists():
        print("Error: agent_tasks.json not found")
        return 1

    manifest = load_json(TASK_FILE)
    modified = False

    # 1. Run generate_ideas.py to pull tasks from game_design.md
    print("[Auto-Improve] Running idea generator...")
    try:
        subprocess.run([sys.executable, "scripts/generate_ideas.py"], check=True)
        # Reload manifest as it might have been modified by generate_ideas.py
        manifest = load_json(TASK_FILE)
    except Exception as e:
        print(f"Error running idea generator: {e}")

    # 2. Run quality metrics and check for test gaps / TODOs
    print("[Auto-Improve] Running quality checks...")
    try:
        # Scan for TODOs/FIXMEs in src/ and add tasks for them
        src_files = list(Path("src").glob("**/*.py"))
        todo_count = 0
        for f in src_files:
            try:
                content = f.read_text(encoding="utf-8")
                for i, line in enumerate(content.split("\n"), 1):
                    if "# TODO:" in line or "# FIXME:" in line:
                        # Extract description
                        desc = line.split("TODO:", 1)[-1].split("FIXME:", 1)[-1].strip()
                        if len(desc) > 5:
                            title = f"Refactor TODO in {f.name}: {desc[:40]}"
                            # Sanitize task ID
                            clean_stem = f.stem.replace("_", "-")
                            task_id = f"todo-refactor-{clean_stem}-{i}"
                            if add_task(manifest, task_id, title, f"Resolve the comment '# TODO: {desc}' in {f.name} line {i}", "meta", "low"):
                                modified = True
                                todo_count += 1
            except Exception:
                pass
        if todo_count > 0:
            print(f"[Auto-Improve] Generated {todo_count} tasks from TODO comments")
            
        # Ruff Linting check
        try:
            ruff_result = subprocess.run(["ruff", "check", "src/", "--format", "json"], capture_output=True, text=True)
            if ruff_result.returncode != 0 and ruff_result.stdout:
                try:
                    violations = json.loads(ruff_result.stdout)
                    lint_count = 0
                    for v in violations[:5]:  # Limit to 5 tasks to avoid spamming
                        code = v.get("code", "LINT")
                        msg = v.get("message", "Lint warning")
                        location = v.get("location", {})
                        row = location.get("row", 1)
                        filepath = v.get("filename", "unknown")
                        filename = Path(filepath).name
                        clean_filename = filename.replace(".", "-").replace("_", "-")
                        task_id = f"lint-{code.lower()}-{clean_filename}-{row}"
                        title = f"Fix lint {code} in {filename}"
                        desc = f"Ruff reported: {msg} in {filepath} line {row}"
                        if add_task(manifest, task_id, title, desc, "meta", "low", acceptance=["Lint warning resolved"]):
                            modified = True
                            lint_count += 1
                    if lint_count > 0:
                        print(f"[Auto-Improve] Generated {lint_count} linting tasks from Ruff")
                except Exception as je:
                    print(f"Failed to parse Ruff json: {je}")
        except FileNotFoundError:
            print("[Auto-Improve] Ruff not installed, skipping linter checks")
    except Exception as e:
        print(f"Error checking code quality: {e}")

    # 3. Run tests and catch failures
    print("[Auto-Improve] Running test suite to catch bugs...")
    try:
        result = subprocess.run(["pytest", "tests/", "--tb=short"], capture_output=True, text=True)
        if result.returncode != 0:
            # We have test failures! Let's generate a bugfix task
            failures = []
            for line in result.stdout.split("\n"):
                if "FAILED" in line:
                    # e.g., tests/test_action.py::test_execute_flee FAILED
                    parts = line.split()
                    if len(parts) >= 2:
                        failures.append(parts[0])
            
            if failures:
                for fail in failures[:3]: # Limit to max 3 failing test tasks to avoid flooding
                    test_name = fail.split("::")[-1]
                    task_id = f"bugfix-{test_name.replace('_', '-')}"
                    title = f"Fix failing test {test_name}"
                    stdout_tail = result.stdout.strip()[-1500:]
                    desc = f"The test {fail} is failing. Investigate and fix the logic so that it passes.\n\nPytest Output Snippet:\n```\n{stdout_tail}\n```"
                    if add_task(manifest, task_id, title, desc, "meta", "medium", acceptance=[f"Test {test_name} passes successfully"]):
                        modified = True
            else:
                # pytest crashed, syntax error, or setup failed
                task_id = "bugfix-pytest-crash"
                title = "Fix test suite runner / pytest crash"
                err_summary = (result.stderr or result.stdout or "Unknown crash").strip()[:300]
                desc = f"The test suite failed to run (return code {result.returncode}). Possible syntax error or broken setup:\n\n{err_summary}"
                if add_task(manifest, task_id, title, desc, "meta", "high", acceptance=["pytest runs successfully"]):
                    modified = True
        else:
            print("[Auto-Improve] All tests passed, no bugfix tasks generated")
    except Exception as e:
        print(f"Error running tests: {e}")

    if modified:
        save_json(TASK_FILE, manifest)
        print("[Auto-Improve] Successfully updated agent_tasks.json with auto-generated tasks")
    else:
        print("[Auto-Improve] No new auto-improvement tasks generated")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
