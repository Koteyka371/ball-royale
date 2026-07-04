1. **Generate Ideas**:
   - Run `run_in_bash_session` to create two ideas in `ideas/idea_idea-553_1.json` and `ideas/idea_idea-553_2.json` with the following scripts:
     `cat << 'EOF' > ideas/idea_idea-553_1.json`
     `{"title": "Multi-Layer Reflect Shield", "description": "A new upgrade allowing the reflect shield to block multiple instances of damage by breaking it into smaller capacity layers."}`
     `EOF`
     `cat << 'EOF' > ideas/idea_idea-553_2.json`
     `{"title": "Shield Blast", "description": "When the reflect shield reaches its capacity or duration ends, it erupts, dealing a portion of the absorbed damage back in an AoE explosion."}`
     `EOF`
   - Verify with `ls ideas/`.

2. **Run Tests**:
   - Run `run_in_bash_session` with the command `PYTHONPATH=src pytest src/` to ensure all changes are correct and no regressions have been introduced.

3. **Pre-commit**:
   - Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.

4. **Submit**:
    - Commit and request code review by running:
      `git add .`
      `git commit -m "[idea-553] Allow upgrading reflect shield capacity and duration"`
      followed by calling `request_code_review`.
