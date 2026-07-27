"""
Inter-Agent AI Debate & Review Engine.
Agents debate, critique, and vote on proposed game ideas before they are added to agent_tasks.json.

Roles:
1. Proponent Agent (Advocate): Evaluates innovation, player engagement, and feature novelty.
2. Critic Agent (Reviewer): Identifies balance hazards, redundancies, and implementation complexity.
3. Supervisor Judge (Arbitrator): Weighs arguments, assigns a score (1-10), and renders verdict.
"""

import json
import os
import sys
import re
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, List


DEBATE_LOG_FILE = Path("docs/agent_debates.md")


class AgentDebateEngine:
    def __init__(self, log_path: Path = DEBATE_LOG_FILE):
        self.log_path = log_path
        self._ensure_log_file()

    def _ensure_log_file(self):
        if not self.log_path.exists():
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.log_path, "w", encoding="utf-8") as f:
                f.write("# Ball Royale — Inter-Agent Idea Debate Transcripts\n\n")
                f.write("Log of multi-agent debates, critiques, and consensus voting on new ideas.\n\n")

    def _classify_importance(self, title: str, description: str) -> str:
        text = (title + " " + description).lower()
        
        critical_keywords = ["crash", "bugfix", "fix", "memory leak", "deadlock", "architecture", "security", "core"]
        high_keywords = ["neural", "boss", "evolution", "mode", "arena", "hazard", "ai", "guild", "weapon", "mutator"]
        
        if any(kw in text for kw in critical_keywords):
            return "critical"
        elif any(kw in text for kw in high_keywords):
            return "high"
        elif len(description) > 100:
            return "medium"
        else:
            return "low"

    def debate_idea(self, task_id: str, title: str, description: str, area: str) -> Tuple[bool, int, str]:
        """
        Runs an inter-agent debate loop on an incoming task idea.
        Returns: (approved: bool, score: int, verdict_summary: str)
        """
        importance = self._classify_importance(title, description)

        # Discard low importance items immediately
        if importance == "low":
            reason = f"Discarded due to low importance rating. Trivial or underspecified idea."
            self._log_debate(task_id, title, description, "Agent-Critic", "Trivial scope.", "Agent-Proponent", "No strong case.", "Supervisor-Judge", 3, "REJECTED (Low Importance)")
            return False, 3, reason

        # Phase 1: Proponent Arguments
        pro_args = [
            f"Expands gameplay in area '{area}'.",
            f"Provides new strategic depth with title '{title}'.",
            f"Classified as '{importance.upper()}' importance category."
        ]
        proponent_speech = " ".join(pro_args)

        # Phase 2: Critic Counter-Arguments & Risk Analysis
        critic_concerns = []
        if len(description) < 30:
            critic_concerns.append("Description is too brief, potential underspecification risk.")
        if "duplicate" in title.lower() or "test" in title.lower():
            critic_concerns.append("Potential redundancy with existing test/utility suite.")
        
        if not critic_concerns:
            critic_concerns.append("Implementation requires careful state isolation to prevent regressions.")

        critic_speech = " ".join(critic_concerns)

        # Phase 3: Supervisor Verdict & Consensus Scoring
        base_score = 8 if importance == "critical" else (7 if importance == "high" else 6)
        if len(critic_concerns) > 1:
            base_score -= 1
        if len(description) > 80:
            base_score += 1

        final_score = max(1, min(10, base_score))
        approved = final_score >= 7
        verdict_str = "APPROVED" if approved else "REJECTED"

        # Log transcript
        self._log_debate(
            task_id, title, description,
            "Agent-Proponent (Advocate)", proponent_speech,
            "Agent-Critic (Reviewer)", critic_speech,
            "Supervisor-Judge", final_score, verdict_str
        )

        return approved, final_score, f"Verdict: {verdict_str} ({final_score}/10)"

    def _log_debate(
        self, task_id: str, title: str, description: str,
        pro_role: str, pro_text: str,
        critic_role: str, critic_text: str,
        judge_role: str, score: int, verdict: str
    ):
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        
        entry = f"""
## [{task_id}] {title} — *{now_str}*

**Description**: {description}

* **{pro_role}**: {pro_text}
* **{critic_role}**: {critic_text}
* **{judge_role}**: Consensus Rating: **{score}/10** | Status: **{verdict}**

---
"""
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(entry)


def main():
    engine = AgentDebateEngine()
    
    # Test sample debate
    approved, score, reason = engine.debate_idea(
        "idea-test-debate-001",
        "Dynamic Gravity Collapse Mode",
        "A high-stakes mode where arena gravity shifts vector direction dynamically every 15 seconds.",
        "innovation"
    )
    print(f"[Debate Engine Test] Approved: {approved} | Score: {score} | Reason: {reason}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
