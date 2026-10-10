---
name: windows-hook-path-testing
description: Test Claude hooks with Windows-style paths (cygpath -m), not Git Bash /c/ paths
type: lesson
scope: project
status: active
updated: 2026-10-09
---
Hook scripts compute relative paths with os.path.relpath; Git Bash paths like /c/Users/... mismatch on Windows Python and silently skip checks.
**Why:** early hook tests falsely passed (exit 0) until paths were converted.
**How to apply:** when testing hooks by hand, build file_path with cygpath -m and set CLAUDE_PROJECT_DIR the same way.
