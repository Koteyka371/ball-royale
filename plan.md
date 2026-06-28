1. **IDEAS INBOX**
   - Execute the following commands:
```bash
mkdir -p ideas
cat << 'IDEA_EOF' > ideas/idea_idea-182_3.json
{
  "title": "Dash Attack Skill",
  "description": "Add a skill for certain ball types that lets them consume all stamina to dash through enemies, dealing heavy damage."
}
IDEA_EOF
cat << 'IDEA_EOF' > ideas/idea_idea-182_4.json
{
  "title": "Exhaustion Effect",
  "description": "Balls with 0 stamina are briefly exhausted, slowing their base speed and lowering their damage until stamina regenerates to at least 20%."
}
IDEA_EOF
ls -la ideas/
```

2. **Run Full Test Suite**
   - Execute `pytest tests/ -m "not interactive_training" -k "not interactive"` to ensure all tests pass and there are no regressions.

3. **Commit Changes Locally**
   - Execute the following Git commands to stage and commit the new ideas:
```bash
git add ideas/idea_idea-182_3.json ideas/idea_idea-182_4.json
git commit -m "Add feature ideas"
```

4. **Pre-commit**
   - Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.

5. **Submit**
   - Execute the `submit` tool to push changes and create the pull request.
