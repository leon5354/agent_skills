"""
UpdateDocs Skill - Auto-changelog on every commit.

Usage as pre-commit hook (scripts/update_changelog.py):
    Called automatically by .githooks/pre-commit before each commit.

Usage as importable skill:
    from skills.update_docs.skill import UpdateDocsSkill
    UpdateDocsSkill(repo_path="/path/to/repo").run()
"""

import subprocess, pathlib, os, datetime

os.environ.setdefault("PYTHONIOENCODING", "utf-8")


class UpdateDocsSkill:
    def __init__(self, repo_path: str = None):
        self.repo = pathlib.Path(repo_path) if repo_path else pathlib.Path(__file__).parent.parent.parent
        self.changelog = self.repo / "CHANGELOG.md"

    def _get_commit_message(self) -> str:
        editmsg = self.repo / ".git" / "COMMIT_EDITMSG"
        if editmsg.exists():
            lines = editmsg.read_text(encoding="utf-8-sig").strip().splitlines()
            return next((l for l in lines if l and not l.startswith("#")), "")
        return "work in progress"

    def run(self) -> bool:
        """
        Prepend today's commit message to CHANGELOG.md and stage it.
        Returns True on success, False if skipped.
        """
        try:
            msg   = self._get_commit_message()
            today = datetime.date.today().isoformat()
            entry = f"## {today} — {msg}\n\n---\n"

            if not self.changelog.exists():
                self.changelog.write_text("# Changelog\n\n---\n", encoding="utf-8-sig")

            text = self.changelog.read_text(encoding="utf-8-sig")
            idx  = text.find("\n---\n")
            if idx == -1:
                text = text + "\n" + entry
            else:
                text = text[:idx + 5] + "\n" + entry + text[idx + 5:]

            self.changelog.write_text(text, encoding="utf-8-sig")
            subprocess.run(
                ["git", "-C", str(self.repo), "add", "CHANGELOG.md"],
                check=True
            )
            return True
        except Exception as e:
            print(f"[update_changelog] skipped: {e}")
            return False


# Entry point when run directly as a hook script
if __name__ == "__main__":
    UpdateDocsSkill().run()
