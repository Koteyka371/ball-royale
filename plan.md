1. **Pre-commit Checks**
   - Call `pre_commit_instructions` tool to execute pre commit checks.
   - Run tests `PYTHONPATH=src pytest tests/ -v`.
   - Remove any remaining temporary files if present.
   - Ensure the new feature ideas `idea_idea-300_1.json` and `idea_idea-300_2.json` exist in the `ideas/` directory.

2. **Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.**
   - Request pre-commit code review using the `request_code_review` tool.

3. **Submit the PR**
   - Push branch to origin.
   - Use `gh pr create --title '[idea-300] Add vision booster powerup' --body 'Task: idea-300' --label 'automated'`
