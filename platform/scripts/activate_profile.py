"""Activate or deactivate a profile overlay.
Usage: python platform/scripts/activate_profile.py <profile> | --off
Activating copies profiles/<profile>/agents/*.md and skills/*/SKILL.md into
.claude/agents/profile-<profile>/ and .claude/skills/, and sets `profile:` in the state file.
Deactivating removes only what the profile installed (recorded in .claude/.profile-manifest)."""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(__file__))
import litecfg as cfg  # noqa: E402

MANIFEST = os.path.join(cfg.ROOT, ".claude", ".profile-manifest")
STATE = os.path.join(cfg.ROOT, "delivery", "state", "lifecycle-state.yaml")


def set_profile(name):
    with open(STATE, encoding="utf-8") as fh:
        lines = fh.readlines()
    with open(STATE, "w", encoding="utf-8", newline="\n") as fh:
        for line in lines:
            fh.write(f"profile: {name}\n" if line.startswith("profile:") else line)


def deactivate():
    if os.path.exists(MANIFEST):
        with open(MANIFEST, encoding="utf-8") as fh:
            for p in (l.strip() for l in fh if l.strip()):
                full = os.path.join(cfg.ROOT, p)
                shutil.rmtree(full, ignore_errors=True) if os.path.isdir(full) else (os.path.exists(full) and os.remove(full))
        os.remove(MANIFEST)
    set_profile("none")
    print("Profile deactivated.")


def activate(name):
    src = os.path.join(cfg.ROOT, "profiles", name)
    if not os.path.isdir(src):
        print(f"Unknown profile: {name}")
        return 1
    deactivate()
    installed = []
    agents = os.path.join(src, "agents")
    if os.path.isdir(agents):
        dest = os.path.join(cfg.ROOT, ".claude", "agents", f"profile-{name}")
        os.makedirs(dest, exist_ok=True)
        for f in os.listdir(agents):
            if f.endswith(".md"):
                shutil.copy(os.path.join(agents, f), dest)
        installed.append(os.path.relpath(dest, cfg.ROOT).replace("\\", "/"))
    skills = os.path.join(src, "skills")
    if os.path.isdir(skills):
        for s in os.listdir(skills):
            if os.path.isdir(os.path.join(skills, s)):
                dest = os.path.join(cfg.ROOT, ".claude", "skills", s)
                shutil.copytree(os.path.join(skills, s), dest, dirs_exist_ok=True)
                installed.append(os.path.relpath(dest, cfg.ROOT).replace("\\", "/"))
    with open(MANIFEST, "w", encoding="utf-8") as fh:
        fh.write("\n".join(installed) + "\n")
    set_profile(name)
    print(f"Profile '{name}' activated. Installed: {', '.join(installed) or 'nothing'}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    if sys.argv[1] == "--off":
        deactivate()
        sys.exit(0)
    sys.exit(activate(sys.argv[1]))
