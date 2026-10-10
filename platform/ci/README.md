# CI Pipelines

Created by `platform-engineer` at G4 for the stack chosen at G3. Required stages, in order:

1. Install with locked dependencies
2. Format and lint
3. Type/static analysis
4. Unit and contract tests (with coverage gate from test-strategy)
5. Architecture tests (`product/architecture-tests/`)
6. Dependency vulnerability and licence scan
7. Secret scan
8. Build artefact (reproducible)
9. End-to-end and accessibility tests (on main and release branches)

Workspace checks to include: `python platform/scripts/validate_state.py` and a check that every
FINAL artifact starts with its status marker.
