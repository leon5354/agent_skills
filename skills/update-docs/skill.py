"""
UpdateDocs Skill - Auto-changelog + document status header management.

Usage as pre-commit hook (scripts/update_changelog.py):
    Called automatically by .githooks/pre-commit before each commit.

Usage as importable skill:
    from skills.update_docs.skill import UpdateDocsSkill
    skill = UpdateDocsSkill(repo_path="/path/to/repo")
    skill.run()  # auto-changelog
    skill.update_status_header("PLAN.md", "Prototype", "PR #5", "synced models")
"""

import subprocess, pathlib, os, datetime, re

os.environ.setdefault("PYTHONIOENCODING", "utf-8")


class UpdateDocsSkill:
    def __init__(self, repo_path: str = None):
        self.repo = pathlib.Path(repo_path) if repo_path else pathlib.Path(__file__).parent.parent.parent
        self.changelog = self.repo / "CHANGELOG.md"

    def _get_commit_message(self) -> str:
        """Extract first non-comment line from COMMIT_EDITMSG."""
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

    def update_status_header(
        self,
        filepath: str,
        status: str,
        reflects: str,
        change_description: str,
        today: str = None,
    ) -> bool:
        """
        Update a document's status header and append a changelog row.

        Args:
            filepath: Relative path to the document (e.g., "PLAN.md")
            status: Document status (Draft, Prototype, Alpha, Beta, Stable, Deprecated)
            reflects: What code/PR state this document matches
            change_description: Short description of what changed
            today: Override date string (YYYY-MM-DD), defaults to today

        Returns True on success, False if skipped.
        """
        try:
            doc = self.repo / filepath
            if not doc.exists():
                print(f"[update_status_header] file not found: {filepath}")
                return False

            today = today or datetime.date.today().isoformat()
            text = doc.read_text(encoding="utf-8-sig")

            # --- Update or insert status header ---
            # Match existing status header block (blockquote starting with > **Status**)
            header_pattern = re.compile(
                r'> \*\*Status\*\*:\s*.+\n'
                r'> \*\*Updated\*\*:\s*.+\n'
                r'> \*\*Reflects\*\*:\s*.+',
                re.MULTILINE
            )

            new_header = (
                f"> **Status**: {status}\n"
                f"> **Updated**: {today}\n"
                f"> **Reflects**: {reflects}"
            )

            if header_pattern.search(text):
                text = header_pattern.sub(new_header, text)
            else:
                # Insert after title (first # line) + blank line
                lines = text.split("\n")
                insert_idx = 0
                for i, line in enumerate(lines):
                    if line.startswith("#"):
                        insert_idx = i + 1
                        # Skip blank lines after title
                        while insert_idx < len(lines) and lines[insert_idx].strip() == "":
                            insert_idx += 1
                        break
                if insert_idx == 0:
                    insert_idx = 0
                lines.insert(insert_idx, new_header + "\n")
                text = "\n".join(lines)

            # --- Append changelog row ---
            changelog_header_pattern = re.compile(
                r'(## Document Changelog\n\n\| Date \| Change \| Source \|\n\|------\|--------\|--------\|\n)',
                re.MULTILINE
            )

            new_row = f"| {today} | {change_description} | {reflects} |"

            if changelog_header_pattern.search(text):
                text = changelog_header_pattern.sub(
                    lambda m: m.group(1) + new_row + "\n",
                    text
                )
            else:
                # Add changelog section at end
                text = text.rstrip() + "\n\n---\n\n## Document Changelog\n\n"
                text += "| Date | Change | Source |\n|------|--------|--------|\n"
                text += new_row + "\n"

            doc.write_text(text, encoding="utf-8-sig")
            subprocess.run(
                ["git", "-C", str(self.repo), "add", str(filepath)],
                check=True
            )
            return True
        except Exception as e:
            print(f"[update_status_header] skipped: {e}")
            return False


# Entry point when run directly as a hook script
if __name__ == "__main__":
    UpdateDocsSkill().run()
