"""Dependency-free readers for lifecycle-state.yaml and gate definitions.
Supports only the flat formats used in this workspace."""
import glob
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
GATE_IDS = ["G0", "G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8"]


def read_state(path=None):
    path = path or os.path.join(ROOT, "delivery", "state", "lifecycle-state.yaml")
    data, section = {}, None
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.split("#", 1)[0].rstrip()
            if not line.strip():
                continue
            m = re.match(r"^(\w[\w-]*):\s*(.*)$", line)
            if m:
                key, val = m.groups()
                if val == "":
                    section = key
                    data[section] = {}
                else:
                    section = None
                    data[key] = val
                continue
            m = re.match(r"^\s+([\w-]+):\s*(.*)$", line)
            if m and section:
                data[section][m.group(1)] = m.group(2)
    return data


def read_gate(gate_id):
    matches = glob.glob(os.path.join(ROOT, "governance", "gates", f"{gate_id}-*.yaml"))
    if not matches:
        raise FileNotFoundError(f"No gate definition for {gate_id}")
    gate, key = {"_path": matches[0]}, None
    with open(matches[0], encoding="utf-8") as fh:
        for raw in fh:
            line = raw.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            m = re.match(r"^(\w+):\s*(.*)$", line)
            if m:
                key, val = m.groups()
                gate[key] = val if val else []
                continue
            m = re.match(r"^\s+-\s+(.*)$", line)
            if m and key and isinstance(gate.get(key), list):
                gate[key].append(m.group(1).strip())
    return gate


def artifact_status(path):
    """Return TEMPLATE / DRAFT / FINAL from the first line marker, or None if absent."""
    with open(path, encoding="utf-8") as fh:
        first = fh.readline()
    m = re.search(r"STATUS:\s*(TEMPLATE|DRAFT|FINAL)", first)
    return m.group(1) if m else None


def resolve(pattern):
    return sorted(glob.glob(os.path.join(ROOT, pattern)))
