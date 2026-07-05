"""
Auto-Improvement Loop.
Runs quality checks, idea generation, test validation, and automatically creates task entries.
"""
import json
import re
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
        name = title.lower()
        name = re.sub(r'ball type\s*-?\s*raises minions', 'necromancer', name)
        name = re.sub(r'ball type\s*-?', 'ball', name)
        name = re.sub(r'\b(system|hazard|event|mode|modifier|weather)\b', '', name)
        name = name.strip()
        name = re.sub(r'[^a-z0-9\s-]', '', name)
        name = re.sub(r'[\s-]+', '_', name)
        slug = name.strip('_')
        
        if area in ("arenas", "arena-mechanics") or "arena" in title.lower() or "trap" in title.lower() or "hazard" in title.lower():
            allowed_paths = [
                f"src/arena/{slug}.py",
                f"src/arena/{slug}.gd",
                f"tests/test_{slug}.py"
            ]
        elif "ui" in title.lower() or "skin" in title.lower() or "prestige" in title.lower() or "quest" in title.lower():
            allowed_paths = [
                f"src/ui/{slug}.py",
                f"src/ui/{slug}.gd",
                f"src/ai/{slug}.py",
                f"tests/test_{slug}.py"
            ]
        else:
            allowed_paths = [
                f"src/ai/{slug}.py",
                f"src/ai/{slug}.gd",
                f"tests/test_{slug}.py"
            ]
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


def extract_test_traceback(pytest_output, test_name):
    """
    Extracts the specific traceback section of pytest_output for a given test_name.
    Pytest splits failure details starting with "_________________ test_name _________________".
    """
    blocks = pytest_output.split("_________________")
    for block in blocks:
        if test_name in block:
            clean_block = block.strip()
            if len(clean_block) > 1500:
                clean_block = clean_block[:1500] + "\n... (truncated)"
            return clean_block
    return pytest_output[-1200:]


def main():
    if not TASK_FILE.exists():
        print("Error: agent_tasks.json not found")
        return 1

    manifest = load_json(TASK_FILE)
    modified = False

    # 0. Process Agent Ideas Inbox
    ideas_dir = Path("ideas")
    if ideas_dir.exists():
        print("[Auto-Improve] Processing ideas inbox...")
        for idea_file in ideas_dir.glob("*.json"):
            try:
                idea_data = load_json(idea_file)
                tasks_to_add = idea_data if isinstance(idea_data, list) else [idea_data]
                for t in tasks_to_add:
                    if "title" in t and "description" in t:
                        max_id = 0
                        for existing_task in manifest.get("tasks", []):
                            tid = existing_task.get("id", "")
                            match = re.search(r'idea-(\d+)', tid)
                            if match:
                                try:
                                    num = int(match.group(1))
                                    if num > max_id:
                                        max_id = num
                                except ValueError:
                                    pass
                        task_id = t.get("id", f"idea-{max_id + 1}")
                        if add_task(manifest, task_id, t["title"], t["description"], 
                                  t.get("area", "innovation"), t.get("risk", "medium"), 
                                  t.get("allowed_paths"), t.get("acceptance")):
                            modified = True
                idea_file.unlink() # Delete the file after processing
            except Exception as e:
                print(f"Error processing idea {idea_file}: {e}")

    # 1. Run generate_ideas.py to pull tasks from game_design.md
    print("[Auto-Improve] Running idea generator...")
    try:
        if modified:
            save_json(TASK_FILE, manifest)
            modified = False
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
                    if "# TO" + "DO:" in line or "# FIX" + "ME:" in line:
                        desc = line.split("TODO:", 1)[-1].split("FIXME:", 1)[-1].strip()
                        if len(desc) > 5:
                            title = f"Refactor TODO in {f.name}: {desc[:40]}"
                            clean_stem = f.stem.replace("_", "-")
                            task_id = f"todo-refactor-{clean_stem}-{i}"
                            if add_task(manifest, task_id, title, f"Resolve the comment '# TO" + "DO: {desc}' in {f.name} line {i}", "meta", "low", allowed_paths=[str(f.as_posix()), "tests/**"]):
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
                        if add_task(manifest, task_id, title, desc, "meta", "low", allowed_paths=[filepath.replace("\\", "/"), "tests/**"], acceptance=["Lint warning resolved"]):
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
        result = subprocess.run(["pytest", "src/", "tests/", "--tb=short"], capture_output=True, text=True)
        if result.returncode != 0:
            failures = []
            for line in result.stdout.split("\n"):
                if "FAILED" in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        failures.append(parts[0])
            
            if failures:
                for fail in failures[:3]: # Limit to max 3 failing test tasks to avoid flooding
                    test_name = fail.split("::")[-1]
                    task_id = f"bugfix-{test_name.replace('_', '-')}"
                    title = f"Fix failing test {test_name}"
                    trace = extract_test_traceback(result.stdout, test_name)
                    desc = f"The test {fail} is failing. Investigate and fix the logic so that it passes.\n\nSpecific Pytest Traceback:\n```\n{trace}\n```"
                    test_file = fail.split("::")[0].replace("\\", "/")
                    if add_task(manifest, task_id, title, desc, "meta", "medium", allowed_paths=[test_file, "src/ai/**", "src/arena/**"], acceptance=[f"Test {test_name} passes successfully"]):
                        modified = True
            else:
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
