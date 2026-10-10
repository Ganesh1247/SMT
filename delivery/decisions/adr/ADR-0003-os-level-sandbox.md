<!-- STATUS: DRAFT -->
# ADR-0003: OS-level learner sandbox (one locked-down container per run) with a role-scoped browser shell

Owner: principal-architect | Date: 2026-10-10 | Reviewer: security-engineer, then staff-code-reviewer, then compliance-auditor | **Decision maker: Founder**

Inputs: Founder decision in chat (2026-10-10): learner Sandbox must be an OS-level restricted environment, one locked-down Docker container per run, Docker Desktop/WSL2 on Windows 11 Home now, Linux/cloud later, accessed through a browser shell with role-scoped, allow-listed tabs for learner, reviewer and auditor; recruiter stays in the HR portal. ADR-0001 section 3 and FF-1; ADR-0002; delivery/G3-solution-design/ux-flows.md sections 2-4 and 10; delivery/G3-solution-design/threat-model.md (T-01a-e, T-02c, T-03b); delivery/G4-delivery-plan/implementation-plan.md (modules `tasks`, `assessment-core`, `probes`, `integrity`; section 10 contingencies); delivery/G4-delivery-plan/delivery-plan.md (D1, R1); delivery/G3-solution-design/contracts/README.md (invariants 2, 3, 15); governance/policies/dependency-policy.md; CLAUDE.md rules 7 and 8.
Design detail: delivery/G3-solution-design/sandbox-environment.md.

## Revision
| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-10-10 | First draft |
| 0.2 | 2026-10-10 | Addresses High findings SR-01 and SR-02 (delivery/G3-solution-design/sandbox-security-review.md). SR-01: runner accepts no paths; closed request schema (UUIDs, enum, size-capped submission to container stdin only); runner builds container arguments from a fixed template; datasets resolved from the runner's own allow-listed read-only store; tests SBX-FF-7..10 added. SR-02: role assignment defined (session/identity claim only; staff roles assigned out of band; learner track is a non-privileged preference; demo-only role switcher; audited changes); tests TAB-FF-6..10 added. Learner tracks (Python developer, Data analyst) added to the design's roles x tabs matrix. All values Proposed. |

## Status
**Proposed. Founder decides.** If accepted, it supersedes ADR-0001 section 3 (task execution engine) in part: the `QueryRunner` port and the SQLite engine controls stay; the execution location moves from the API process into a per-run container. ADR-0001 FF-1 is extended, not removed. Every numeric limit in this ADR and in the design document is **proposed** until measured in SLICE-003.

## Context and forces
| Force | Source | Implication |
|---|---|---|
| Founder requires OS-level isolation for learner code, not only engine-level controls | Founder decision 2026-10-10 | In-process SQLite (ADR-0001 s3) is no longer sufficient on its own |
| Learner SQL is hostile input (recursive CTE bombs, `ATTACH`, huge results, reads of hidden data) | Threat model T-01a-d; R1 | Kernel-enforced limits on CPU, memory, processes, files and network, plus the existing engine controls |
| Development and demo machine is Windows 11 Home | Founder | No Hyper-V backend, no Windows containers; Docker Desktop with the WSL2 backend only; no rootless Docker; bind mounts from Windows paths (this repo sits on OneDrive) are slow and unreliable |
| Linux or cloud later | Founder | The adapter must be portable to a Linux Docker or OCI runtime without code change in `tasks` |
| 24-hour build, 3 developers | Implementation plan s1 | Extra infrastructure must be small, scripted and pre-installed before H0 |
| Rule 7 modular monolith; rule 8 dependencies declared, no secrets | CLAUDE.md | The container must sit behind the existing port; any new process or tool needs an ADR and register entry |
| Roles must not be selectable by the client; recruiter never touches the Sandbox | Founder; contracts README; ADR-0002 AT-02 | Role comes from the authenticated session; recruiter credentials are rejected by the shell |
| No timers or speed indicators shown to learners | ux-flows G-8, A11Y-4 | Run wall-clock limits are execution limits, never shown as a countdown |
| No silent degradation | Founder; rule 5 evidence over claims | Any fallback is explicit, configured and labelled |

## Options considered
| Option | Pros | Cons | Cost to reverse |
|---|---|---|---|
| **A. One locked-down Docker container per run, started by a narrow runner service (chosen)** | Kernel-enforced isolation (namespaces, cgroups, seccomp, dropped capabilities, no network, read-only root); same mechanism on Windows (WSL2 VM) and Linux/cloud; fresh container per run gives no shared state by construction; also unlocks a Python ladder later (D1); well-known, testable with `docker inspect`; the WSL2 VM adds a second boundary on the Founder's machine | Cold start per run (indicative 0.5 to 2 s on Docker Desktop, unmeasured); Docker Desktop must be installed and running on every developer and demo machine; Docker engine access is root-equivalent, so the component that holds it must be isolated from the API (runner service); image supply chain to manage; more moving parts in a 24 h build | Medium: `QueryRunner` port is unchanged, so going back to in-process is a configuration switch; the runner service and image are discarded |
| B. Restricted OS user plus job limits (Windows Job Objects / AppContainer; Linux setrlimit, separate uid, cgroup) | No Docker; fast start | Two different, platform-specific implementations (Windows now, Linux later); Windows Job Objects and AppContainer need native API code (ctypes/pywin32, new dependency) and are hard to verify for file and network denial; no read-only filesystem view; weaker and less familiar escape story | Medium |
| C. Micro-VM per run (Firecracker, Kata, Cloud Hypervisor) | Strongest isolation (separate kernel) | Needs KVM; on Windows 11 Home only possible via nested virtualisation inside WSL2, unsupported or fragile; large setup and image-building effort; cannot be delivered in 24 h | High |
| D. Keep in-process SQLite (ADR-0001 s3 as written) | Zero setup; already designed; fastest | Not OS-level, so does not meet the Founder requirement; a pathological query costs API CPU until the step budget trips; an engine bug is an API-process compromise | Low |
| (Variant of A, open) gVisor `runsc` runtime under Docker | Adds a user-space kernel between learner code and the host kernel | Not supported by Docker Desktop on Windows without a separate Docker engine inside a WSL2 distro; extra setup; candidate for Linux/cloud phase | Low (runtime flag) |

## Decision (proposed)
Adopt **Option A**. Learner-supplied code (SQL for the MVP ladder) runs only inside a fresh, locked-down, single-use container: non-root, read-only root filesystem, tmpfs scratch only, no network, all capabilities dropped, no-new-privileges, default seccomp profile, pids/memory/CPU/ulimit/wall-clock limits, a read-only seeded dataset, a size-capped JSON result on stdout, and forced kill-and-remove on every exit path. The image is built from a repository Dockerfile with a base pinned by digest and contains only the runner entrypoint (standard library only).

Containers are started by a **narrow runner service**: a small, stateless process with one endpoint (`POST /runs`) that accepts a validated run request, holds the only Docker access, and has no domain logic. **The runner accepts no paths and no container options (SR-01, proposed):** the request is a closed schema of `run_id` (UUID), `task_id` and `dataset_id` (opaque UUIDs that the runner resolves against its own allow-listed, read-only, hash-verified dataset store), `limits_profile` (closed enum) and the size-capped submission text, which the runner forwards only to the container's stdin. Any other field, unknown enum value, non-UUID, unknown ID pair or oversize submission is rejected. The runner builds every container argument itself from a fixed template plus constants selected by the enum; no request field ever reaches argv, environment, labels, mounts or file names. A compromised API can therefore at most ask the runner to execute text against a pre-published dataset under a pre-defined profile. Schema and store: sandbox-environment.md s3.0. The API process never mounts or opens `docker.sock` (or the Docker Desktop named pipe) and never imports a Docker client. In `tasks`, a new infrastructure adapter `ContainerQueryRunner` implements the existing `QueryRunner` port by calling the runner service. Probes and Level 4 use the same port (T-01d: no second executor). Hidden checks and expected outputs are computed outside the container by server-authored SQL and never enter it.

The SQLite engine controls from ADR-0001 s3 (authorizer deny-by-default, single statement, step budget, `query_only`, row and size caps) **remain inside the container** as defence in depth.

The learner, reviewer and auditor reach their screens through one **browser shell** whose tabs are allow-listed per role. The role comes only from the authenticated session; every API route declares the tab and role(s) it serves and is denied by default. Recruiters have no session type in the shell.

**Role assignment (SR-02, proposed):** the role is a server-side claim on the session, issued by `identity` from its own records; it is never read from the client. Self sign-up always creates a `learner`; `reviewer` and `auditor` are assigned out of band by an administrator or the identity provider and are never offered at sign-up or in any UI selector. A learner's **track** (Python developer or Data analyst) is a separate preference field that selects a workspace tab manifest and grants no privilege. A role switcher exists only in demo mode, is labelled "Demo only", signs in as a seeded demo identity through the server, and its route is not registered outside demo mode. Every role or track change is validated server-side and written as an append-only, hash-chained identity audit event. Detail: sandbox-environment.md s4.1.

Why A: it is the simplest option that is OS-level, works on Windows 11 Home today, and carries unchanged to Linux/cloud. B is platform-specific and harder to verify; C cannot be delivered on the current machine or in 24 h; D does not meet the requirement.

### Rule 7 position (for reviewer and Founder)
The runner service is a second process. The architect's position is that it is a **privilege-separation helper for one infrastructure adapter**, not a bounded context: it owns no data, no domain rules and no module `api/`; the monolith remains one deployable unit for all business capabilities (ADR-0002 Option B unaffected). This ADR is the "ADR proves the need" record for that process. If the reviewer or the Founder considers it a distribution under rule 7, that question goes to `delivery/decisions/escalations/`.

### Fallback when Docker is unavailable
- Mode is set by configuration only: `SANDBOX_MODE=container` (default) or `SANDBOX_MODE=in_process` (proposed names).
- In `container` mode, if Docker or the pinned image is unavailable, runs **fail closed**: the learner sees "We could not run your query right now. Your work is saved. Try again." and the event is logged. There is **no automatic fallback**.
- `in_process` mode is the ADR-0001 s3 engine run in a separate worker process. It must be switched on deliberately, is logged at startup, is reported by the health endpoint, and shows a persistent banner in every shell tab: "Reduced isolation mode: queries run without the container sandbox." (wording proposed; ux-architect to confirm). Each run record stores `isolation_mode`. Whether the ledger event must also carry it is a contract question (sandbox-environment.md, open question Q7).
- Second fallback (unchanged from implementation plan s10): fixed query set, no free-form SQL.

## Effect on other decisions
| Decision | Effect |
|---|---|
| ADR-0001 s3 | Partly superseded: execution location changes; engine, port and controls retained. "Python or general code execution in a container" moves from rejected to possible later (D1 still open). |
| ADR-0001 FF-1 | Kept and run against the container adapter; extended by SBX-FF-1..6 below. |
| ADR-0001 s6 | New dependencies to declare: Docker Desktop (tool, licence terms to verify), base image pinned by digest, optional image scanner. Proposal: call the Docker CLI with a fixed argument list via `subprocess` (no shell) from the runner only, so no new Python library. |
| ADR-0002 | Option B unchanged. Under Option A the runner is still one helper process beside the Sandbox system. AT-02 extended: the shell rejects recruiter credentials. |
| Implementation plan s10 | Trigger "Sandbox runner unsafe or slow at H10" now has two steps: switch to labelled `in_process` mode, then fixed query set. |
| Threat model | New threats S-1..S-11 (sandbox-environment.md s7) for security-engineer to merge. |

## 24-hour hackathon cost (estimates, not measurements)
| Item | Indicative effort |
|---|---|
| Dockerfile, pinned base, entrypoint script, build script | 1 to 1.5 dev-hours |
| Runner service (one endpoint, lifecycle, kill/remove, reaper, caps) | 1.5 to 2 dev-hours |
| `ContainerQueryRunner` adapter, mode switch, banner | 0.5 to 1 dev-hour |
| Container-level escape and config tests | 1 to 1.5 dev-hours |
| Role-scoped tab manifest, route policy middleware, denial tests, CSP | 1.5 to 2.5 dev-hours |
| **Total** | **about 5.5 to 8.5 dev-hours** of roughly 48 build hours |

Pre-event work (outside the 24 h clock if the profile allows; Founder to confirm): enable virtualisation and WSL2, install Docker Desktop on every machine, pull and pin the base image so the build works offline, check `.wslconfig` memory. SLICE-003 grows from M to L (as D1 predicted); SLICE-001 grows from S to M.

## Windows 11 Home constraints
- WSL2 backend only; containers run in the Docker Desktop Linux VM. Isolation boundary is container plus VM.
- Rootless mode and `userns-remap` are not available as normal Docker Desktop settings; containers run with a non-root uid inside, but a container root escape would land as root inside the VM. gVisor needs a separate engine in a WSL2 distro (open question).
- Any process running as the Founder's Windows user can reach the Docker Desktop engine pipe. On the laptop, API-versus-runner separation is therefore enforced by code and tests (SBX-FF-5), and by running the API in a container without the pipe if the compose topology is chosen; on Linux it is enforced by separate OS users. Stated plainly so it is not over-claimed.
- Bind mounts from Windows paths, especially OneDrive, are slow; datasets are delivered from a runner-owned directory outside OneDrive, or via stdin (open question Q4).
- Docker Desktop licence: free for personal and small-business use under Docker's thresholds at time of writing; Founder to confirm eligibility.

## Consequences
Positive
- Learner code is contained by the kernel and the VM, not only by engine settings; an engine bug no longer means an API compromise.
- Same adapter runs on Linux/cloud; gVisor or a micro-VM runtime can be added later behind the same runner.
- A Python ladder becomes technically possible without redesign.
- Role-to-tab access is a server-side, testable table instead of UI convention.

Negative
- Per-run latency rises (cold start); learner "Evaluating" state (ux-flows 4.6) must cover it.
- Docker becomes a hard prerequisite for full isolation; demo machines need preparation.
- One more process to start, monitor and test; root-equivalent Docker access must be guarded.
- Image supply chain must be pinned and scanned.
- (SR-01) Per-learner datasets, probe variants and Level 4 mutation variants must be pre-published to the runner store, which turns "per-learner seed" into "per-learner assignment from a pre-generated pool" (pool size proposed, Q12 in the design). Seed copying across learners who share a pool entry becomes possible; `integrity` fingerprints must account for it.
- (SR-02) The Python developer track needs code execution in the container, which depends on Founder question Q1 (D1); until Q1 is answered, the Python track tabs are design only.

Follow-up work
- security-engineer: review S-1..S-11 and merge into threat-model.md; define custom seccomp profile if the default is judged insufficient.
- principal-architect: dependency-register entries (Docker Desktop, base image digest, scanner if adopted); update architecture-overview deployment table and AT list; update SLICE-001 and SLICE-003 scope in the delivery plan after Founder decision.
- ux-architect: copy for the reduced-isolation banner, run-timeout message and "not available" page.
- Founder: Q1 to Q12 in sandbox-environment.md s8.

## Fitness function / verification
| ID | Check | Where |
|---|---|---|
| FF-1 (ADR-0001, kept) | SQL escape suite (writes, `ATTACH`, `PRAGMA` writes, `load_extension`, multiple statements, endless recursive CTE, huge cross join) refused or stopped within budget, run through `ContainerQueryRunner` | SLICE-003 |
| SBX-FF-1 | Container config assertion: for a live run, `docker inspect` shows non-root user, `ReadonlyRootfs=true`, `NetworkMode=none`, `CapDrop=[ALL]`, empty `CapAdd`, `no-new-privileges`, seccomp not `unconfined`, `Privileged=false`, pids, memory and CPU limits set, only the dataset mount and it is read-only, no Docker socket mount | SLICE-003 |
| SBX-FF-2 | Container-level escape suite using a test-only entrypoint in the same image with the same flags: outbound network, `host.docker.internal`, write to `/` and `/data`, fork bomb, memory hog, `setuid`/`su`, `mount`, raw socket, `ptrace`, read of `/proc/1/environ` for secrets, presence of `docker.sock`, stdout flood; every attempt fails or is killed and the runner returns a bounded error | SLICE-003 |
| SBX-FF-3 | No state between runs: run A writes a marker to tmpfs, run B cannot see it; labelled container count returns to baseline after success, timeout, OOM and runner crash (reaper) | SLICE-003 |
| SBX-FF-4 | Runner refuses to start a container whose image digest differs from the pinned digest | SLICE-003 |
| SBX-FF-5 | API packages import no Docker client and no `subprocess`; compose/run config gives the API no Docker socket or pipe; only the runner package references the Docker CLI | Architecture tests, every slice |
| SBX-FF-6 | With Docker stopped and `SANDBOX_MODE=container`, runs fail closed (no result, no silent fallback); with `SANDBOX_MODE=in_process`, health endpoint, every shell page and every run record show the reduced-isolation label | SLICE-003, SLICE-001 |
| TAB-FF-1 | Every registered API route has a tab and role policy; an undeclared route fails the test suite at startup | SLICE-001 |
| TAB-FF-2 | Roles x tabs matrix test generated from sandbox-environment.md s4: every disallowed (role, tab) pair is denied for the tab manifest, the shell route and each API route | SLICE-001, extended per slice |
| TAB-FF-3 | Direct URL and direct API calls: a learner requesting another learner's object, or any role calling another role's API, gets the uniform denial with no data and no existence signal | SLICE-001 |
| TAB-FF-4 | Client-supplied role (header, query string, body, local storage) has no effect; recruiter (HR) credentials are rejected by the shell API | SLICE-001 |
| TAB-FF-5 | CSP and security headers present and exact on every shell response; no inline script; no iframe; external navigation blocked | SLICE-001 |
| SBX-FF-7 | Path rejection: run requests carrying a path or path-like value in any field (`../`, absolute POSIX or Windows paths, UNC, `file:` URL, `/var/run/docker.sock`), or an ID not in the store manifest, are rejected before any Docker call; no container is created | SLICE-003 |
| SBX-FF-8 | Closed enum: unknown, empty, case-variant or numeric `limits_profile` values are rejected | SLICE-003 |
| SBX-FF-9 | Oversized submission (cap + 1 byte, and invalid UTF-8) is rejected without starting a container; submission text never appears in argv, environment, labels or file names (checked with `docker inspect` and the runner's command log) | SLICE-003 |
| SBX-FF-10 | Extra fields (for example `image`, `mounts`, `volumes`, `privileged`, `network`, `env`, `cmd`) are rejected; the generated container argument list is identical to the fixed template for every enum value (golden test) | SLICE-003 |
| TAB-FF-6 | Sign-up cannot set a role: sign-up requests with `role`, `roles` or similar fields are rejected, and every self-registered account is `learner` | SLICE-001 |
| TAB-FF-7 | Tampered client role claim rejected: a modified, replayed or forged session cookie or token, or a client-sent role value, yields the uniform denial and no role change | SLICE-001 |
| TAB-FF-8 | Track change does not alter privileges: changing track changes only the workspace manifest; a learner gains no staff tab or route; a staff session cannot obtain learner track tabs | SLICE-001 |
| TAB-FF-9 | Demo role switcher route is not registered and its UI is absent when demo mode is off; when on, it is labelled "Demo only" and only switches between seeded demo identities | SLICE-001 |
| TAB-FF-10 | Every role or track change writes one identity audit event (actor, subject, old, new, time, hash chain); a change that is not audited fails the test | SLICE-001 |
