import json
import re
from pathlib import Path
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.auto_improve_loop import load_json, save_json, add_task

TASK_FILE = Path("agent_tasks.json")

def get_files_to_sync():
    files = []
    ai_dir = Path("src/ai")
    if ai_dir.exists():
        for py_path in ai_dir.glob("*.py"):
            if py_path.name == "__init__.py":
                continue
            gd_path = py_path.with_suffix(".gd")
            if gd_path.exists():
                files.append((str(py_path), str(gd_path)))
    return files

def extract_python_methods(filepath):
    try:
        content = Path(filepath).read_text(encoding="utf-8")
        # Find all def method_name(self, ...)
        methods = re.findall(r'def\s+(\w+)\s*\(', content)
        # Exclude private built-ins like __init__
        return {m for m in methods if not m.startswith("__")}
    except Exception:
        return set()

def extract_gdscript_methods(filepath):
    try:
        content = Path(filepath).read_text(encoding="utf-8")
        # Find all func method_name(...)
        methods = re.findall(r'func\s+(\w+)\s*\(', content)
        return set(methods)
    except Exception:
        return set()

def run_sync_check():
    print("[Check-Sync] Comparing Python and GDScript AI layers...")
    
    if not TASK_FILE.exists():
        print("[Check-Sync] agent_tasks.json not found, aborting.")
        return
        
    manifest = load_json(TASK_FILE)
    modified = False

    for py_file, gd_file in get_files_to_sync():
        py_path = Path(py_file)
        gd_path = Path(gd_file)
        
        if not py_path.exists() or not gd_path.exists():
            print(f"  Warning: {py_file} or {gd_file} does not exist, skipping.")
            continue
            
        py_methods = extract_python_methods(py_path)
        gd_methods = extract_gdscript_methods(gd_path)
        
        missing_in_gd = py_methods - gd_methods
        if missing_in_gd:
            print(f"  {gd_path.name} is missing methods from {py_path.name}: {missing_in_gd}")
            for method in missing_in_gd:
                task_id = f"sync-gd-{gd_path.stem}-{method.replace('_', '-')}"
                title = f"Sync GDScript: Implement '{method}' in {gd_path.name}"
                desc = (f"The Python class in {py_path.name} implements '{method}', "
                        f"but the GDScript counterpart {gd_path.name} is missing it. "
                        f"Please implement the same logic in GDScript.")
                if add_task(manifest, task_id, title, desc, "content", "medium", allowed_paths=[gd_file]):
                    modified = True
        else:
            print(f"  {gd_path.name} is in sync with {py_path.name}")

    if modified:
        save_json(TASK_FILE, manifest)
        print("[Check-Sync] Successfully created synchronicity tasks!")
    else:
        print("[Check-Sync] All layers are perfectly synchronized.")

if __name__ == "__main__":
    run_sync_check()
