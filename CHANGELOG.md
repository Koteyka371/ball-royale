# Changelog

All notable changes to Ball Royale will be documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added
- Battle simulation engine (50-1000 balls) — `tests/simulate_battle.py`
- AI performance benchmark — `tests/benchmark_ai.py`
- Ball type configs — `configs/ball_types.json`
- Content generator from JSON — `scripts/generate_content.py`
- Code quality metrics — `scripts/quality_metrics.py`
- Changelog (this file)

### Changed
- Jules prompt now enforces self-evolution after each task
- Jules must run simulation and quality checks before creating PR

## [0.1.0] - 2026-06-05

### Added
- BallBrain architecture (Perception → Emotion → Decision → Action)
- GDScript implementation — `src/ai/ball_brain.gd`
- Python implementation — `src/ai/ball_brain.py`
- Unit tests for BallBrain — `tests/test_ball_brain.py`
- GitHub Actions CI pipeline
- Jules infinite loop workflow with self-improvement
- Auto-merge for Jules PRs
- 37 initial tasks in `agent_tasks.json`
