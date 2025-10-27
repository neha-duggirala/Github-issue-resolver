user_prompt = """
--- Found 2 Commits in PR #1 ---

1. SHA: dd46be1 | Author: neha-duggirala | Message: "readme auto generate init"
  --- Detailed Stats for Commit (dd46be1) ---
  Commit Message: readme auto generate init
  Author: neha-duggirala
  Date: 2025-10-20

  --- Difference Statistics (Diff Stats) ---
  Total Changes: 42
  Additions (++): 42
  Deletions (--): 0

  --- Files Modified ---
  - File: readme.md
    Lines Added: +42, Lines Deleted: -0
    Patch (snippet):
    @@ -0,0 +1,42 @@
+# GitHub Issue Resolver
+
+A small tool to help automate, triage, and manage GitHub issues for a repository.
+
+## Features
+- Create, label, and close issues based on simple rules
+...

2. SHA: 593208c | Author: neha-duggirala | Message: "add commands for environment setup and initialization"
  --- Detailed Stats for Commit (593208c) ---
  Commit Message: add commands for environment setup and initialization
  Author: neha-duggirala
  Date: 2025-10-27

  --- Difference Statistics (Diff Stats) ---
  Total Changes: 9
  Additions (++): 9
  Deletions (--): 0

  --- Files Modified ---
  - File: commands.txt
    Lines Added: +9, Lines Deleted: -0
    Patch (snippet):
    @@ -0,0 +1,9 @@
+To start env:
+.venv\Scripts\Activate.ps1
+
+        .venv\Scripts\activate.bat
+
+
+To init uv
+
+uv init
\ No newline at end of file...
==================================================
"""


system_prompt = """You are an expert software developer with deep knowledge of GitHub's API and best practices for code review
and repository management. 
Your task is to analyze the provided commit data from a GitHub Pull Request (PR) and generate a review comment. you will be replacing a code reviewer or your comments will be an assistant for other reviewers.

Your summary report should include the following sections:
1. Overview: A brief summary of the PR's purpose based on the commit messages.
2. code smells: Identify any potential code smells or areas of concern in the commits.
3. Suggestions: Provide actionable suggestions for improvements or changes that could enhance the quality of the code
4. Questions: Pose any relevant questions that the author or team should consider regarding the changes made.

When generating your review comment, ensure that it is clear, concise, and constructive. Use a professional and respectful tone, and focus on providing value to the author and the team.
Your review comment should be formatted in markdown for better readability on GitHub.
Your review comment should be based solely on the commit data provided below:

"""
