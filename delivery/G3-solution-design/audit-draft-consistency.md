<!-- STATUS: DRAFT -->
# Gate Audit Report: draft consistency audit, G1-G4

Owner: compliance-auditor | Gate: G1, G2, G3, G4 (pre-review of DRAFT artifacts) | Version: 0.1 | Date: 2026-10-10 | Reviewer: Founder (decision); auditor is independent of all authors
Inputs: delivery/G0-intake/final-solution-approach.md, curated-pitch-content.md, problem-statement-SAMARTHA-02.txt (Part A); delivery/G1-discovery/feasibility-assessment.md; delivery/G2-product-definition/prd.md, success-metrics.md; delivery/G3-solution-design/architecture-overview.md, ux-flows.md, threat-model.md, contracts/; delivery/decisions/adr/ADR-0001-stack.md, ADR-0002-three-systems.md; delivery/G4-delivery-plan/delivery-plan.md, implementation-plan.md, test-strategy.md

> No upstream artifact is FINAL and G0 is not approved, so this is a consistency audit of drafts, not a gate-closing audit. No artifact, state file or code was edited. Note: this file was written at the path requested by the Chief of Staff, outside the auditor's default output folder (`delivery/G6-assurance-audit/`).

## Gate and scope
Gates G1-G4, all artifacts listed above, audited 2026-10-10 by compliance-auditor. Checks requested: requirement traceability, score-gate rule, rule 7 and ADR-0002, threat-model contract changes C1-C7, claim hygiene, feasibility vs promises, rules 5 and 8, `product/` emptiness.

## Automated checks
| Check | Result |
|---|---|
| `validate_state.py` | "State valid. project=unassigned profile=none current_gate=G0". Note: PRD A7 assumes profile `hackathon-24h` is active; state says `none`. |
| `gate_check.py G1` | NOT READY: G0 `in_progress`; `market-and-user-research.md` missing; feasibility DRAFT |
| `gate_check.py G2` | NOT READY: G1 `pending`; prd.md and success-metrics.md DRAFT |
| `gate_check.py G3` | NOT READY: G2 `pending`; ux-flows, architecture, threat model, ADR-0001, ADR-0002 DRAFT; `dependency-register.md` missing |
| `gate_check.py G4` | NOT READY: G3 `pending`; delivery-plan.md and test-strategy.md DRAFT |
| Re-run `contracts/canonical_hash.py` (auditor) | `16/16 checks passed`; hash `sha256:cd2f785f...c0d6` matches hash-canonicalisation.md "Test vector" |
| Re-run `contracts/validate_examples.py` (auditor) | `0 failure(s)` |
| `product/` contents | Only `README.md` and five `.gitkeep` files. No code. Rule 1 respected. |
| Secret pattern grep over `delivery/` and `product/` | No hits (consistent with threat-model s3.7 read-only scan) |
| `platform/quality-commands.json` | `"on_edit": []` (not configured; G3 exit criterion) |
| `platform/ci/` | `README.md` only; no pipeline (G4 exit criterion) |

## Exit criteria assessment
| Gate | Criterion | Evidence | Met? |
|---|---|---|---|
| G1 | Target users and JTBD with sources | No `market-and-user-research.md`; feasibility s0 "reused, not re-researched" | N |
| G1 | At least 3 alternatives or competitors compared | Feasibility has no competitor section (headings s0-s8) | N |
| G1 | Assumptions with validation method | Feasibility s5 | Y |
| G1 | Technical, legal, data feasibility with risk rating | Feasibility s1 matrix, s3, s6 | Y (legal all UNVERIFIED, s3) |
| G1 | Every claim sourced or labelled | Feasibility evidence tags FACT/FACT-G0/INFERENCE/ASSUMPTION; s4 verification log | Y |
| G2 | Unique IDs, MoSCoW, testable criteria | PRD s5, s6 Given/When/Then | Y |
| G2 | NFRs (performance, security, a11y, availability) | PRD s6 NFR-001..007; availability only as NFR-007 demo resilience | Partial |
| G2 | Scope and non-goals | PRD s4 | Y |
| G2 | Metrics with baseline, target, method | success-metrics.md "Metrics" table | Y |
| G2 | Traceable to G1 findings | PRD header: "G1 research is not a separate FINAL artifact yet"; REQ-007 contradicts feasibility s2.4 (F-06) | N |
| G3 | Module map with owners and api surfaces | Architecture s2 | Y |
| G3 | Stack via ADRs with alternatives and consequences | ADR-0001, ADR-0002 | Y (both Proposed) |
| G3 | Data model and contracts | Architecture s4, s5; contracts/ | Partial (C1-C7 open, F-04; no contract for profile, appeals, verify-receipt: ux-flows s12 items 1, 4) |
| G3 | UX flows cover all Must requirements, with a11y | ux-flows s10, s11.2 keyed to tiers, not REQ IDs | Partial |
| G3 | Threat model covers every trust boundary | threat-model s2 TB1-TB10 | Partial (modelled on Option A topology, F-03) |
| G3 | quality-commands.json configured | Empty | N |
| G3 | Every PRD Must maps to a module and a flow | Architecture s9 omits REQ-022, NFR-005, NFR-007 | N |
| G4 | Slices with IDs, REQ links, owner, acceptance tests | delivery-plan s4 | Partial (F-01) |
| G4 | Critical path and dependencies | delivery-plan s6 | Y |
| G4 | Risk register | delivery-plan s9 | Y |
| G4 | Test strategy covers unit, contract, e2e, perf, security, a11y | test-strategy s2 | Y |
| G4 | CI pipeline in platform/ci/ | README only | N |
| G4 | DoD confirmed | delivery-plan s10 | Y |

## Consistency checks

### 1. Requirement IDs (PRD vs delivery-plan s3/s11 vs test-strategy s5)
| ID | Pri | PRD | Plan s3 | Plan s11 slice | Arch s9 | Test-strategy s5 |
|---|---|---|---|---|---|---|
| REQ-022 No hire output, no proxy ranking | **Must** | Yes | Missing | **None** | Missing (AT-11 covers in part) | **None** |
| REQ-023 Auditor view | Should | Yes | Missing | None | Missing | None |
| NFR-005 Reproducibility | **Must** | Yes | Missing | **None** | Missing | **None** |
| NFR-006 Latency p95 < 5 s | Should | Yes | Missing | None | Missing | None (s2 perf row says "under 1 s"; arch s1 says "3 s p95") |
| NFR-007 Demo resilience | **Must** | Yes | Missing | **None** (SLICE-018 implied, not mapped) | Missing | None |
| REQ-014..017 | Should | Yes | Yes | Not in s11 (slices 013-016 exist in s4) | Yes | **None** |
| REQ-019 | Could | Yes | Yes | No slice | Gap noted (Q10) | None |
| NFR-003 | **Must** | Yes | Yes | SLICE-015 only, which is cut-order 5 (s8) | Gap noted (Q6) | Yes |

Test-strategy s5 "17 of 17 (13 REQ + 4 NFR)" counts only the provisional plan IDs; the PRD has 23 REQ + 7 NFR. PRD change log already flags "delivery-plan s11 coverage needs update". Plan s11 claim "Every Must requirement maps to at least one slice" is false against the PRD.

### 2. Score-gate rule
| Artifact | Rule stated |
|---|---|
| PRD s3 rule 1, REQ-006 | Score and band update **only after all four levels** pass, per competency |
| curated-pitch-content.md "Score rule" | All four levels |
| ux-flows s4.1 step 8 | All four levels |
| delivery-plan s3 REQ-006 | "Levels 1 to 3 progression ... gated score update"; SLICE-009 "L1-L3 ... Score unchanged until all levels pass" (ambiguous) |
| test-strategy T-006a | "score unchanged until all **L1-L3** passed"; XS-4 pass criterion "changes **only after L3**" (contradicts PRD) |
| architecture s4 "Score gate", Q3 | Left open |
| contracts/shared-evidence.schema.json | `proficiency` is **required**; no way to express "no estimate yet" for a competency with `levels_passed` < 4 |
| ux-flows s4.2 step 5 | L4 result "Evaluated, reviewable, not pass/fail", but REQ-006 needs an L4 pass to trigger the update |

Consequence: under the PRD rule, the band (REQ-009, never-cut) moves only if SLICE-010 (Level 4, risk H, feasibility s2.4 "Low") works. The never-cut list (plan s8) omits 009 and 010, so the demo's band depends on a cuttable, riskiest slice.

### 3. Rule 7 and ADR-0002
Architecture s1/s2 baseline is ADR-0002 Option B (modular monolith with three bounded-context groups, `api/` facades, AT-01..AT-13): compliant. ADR-0002 "Status" and "The conflict, stated explicitly" correctly refuse to treat Option A as accepted without a Founder-approved rule-7 exception. Inconsistent downstream: implementation-plan s1/s7/S4 ("three stubs run via one compose command"), threat-model header ("three systems ... talking REST with service API keys"; TB4, TB7, T-06g, T-07*), test-strategy s4 ("Three services via compose") all assume Option A. Module names also differ (implementation-plan s2 has no `competency` module; architecture s2 does).

### 4. Threat-model C1-C7 vs contracts
| # | Reflected? | Evidence |
|---|---|---|
| C1 per-recipient event IDs | No | shared-evidence.schema.json `evidence_items[].event_id` (uuid) and `receipt_hash` still global, required |
| C2 fields conditional on `scope.include` | No | `proficiency`, `method_counts`, `understanding_status`, `evidence_items` all in top-level `required` |
| C3 `event_id`, `recorded_at` in hash | No | hash-canonicalisation.md rule 2 field list excludes both; rule 8 exempts `event_id` and `ledger` |
| C4 `maxItems` on `evidence_items` | No | no `maxItems` |
| C5 keyed `submission_ref` | No | evidence-event.schema.json `submission_ref` pattern `^sha256:` |
| C6 README: Trust rejects read-only fields | No | README invariant 11 only covers `ledger` block; no mention of `event_id`, `grant_id`, `status`, `source_system` derivation |
| C7 idempotency semantics (409) | No | README invariant 10 only "never stored twice" |
None of C1-C7 is applied; O-11 decision is open. T-04a (Critical, no learner authentication) has no slice or PRD NFR.

### 5. Claim hygiene
No artifact claims scores predict hiring; PRD s1 "Standing label", success-metrics preamble, pitch header and s85, ux-flows G-3, architecture header, shared-evidence `labels.experimental: const true` all carry the experimental/no-prediction label. No mock-up is presented as working; test-strategy s5 marks every product test "Not run". Risk: curated-pitch-content.md "Innovation" item 4 states in present tense "Level 4's new constraint is generated from the learner's own code", a mechanism feasibility rates Low and recommends stubbing.

### 6. Feasibility recommendations vs promises
| Feasibility recommendation | PRD | Plan | Pitch |
|---|---|---|---|
| Cut live video (s2.10, s7.2) | Could, non-goal (REQ-021): aligned | SLICE-021, cut order 1: aligned | Could, cut first: aligned |
| Stub L4 mutation follow-ups (s2.4, s7.2) | **REQ-007 Must** "mutation-generated follow-up" | SLICE-010 Must, on critical path | "Mutation-driven follow-ups" headline innovation |
| Band illustrative, "not calibrated" label (s2.5, s0.3) | REQ-009 has no "illustrative/not calibrated" criterion; only Q8 mentions it | SLICE-006 acceptance has no such label | "Honest skill estimate", no illustrative label |
| Must tier at upper bound for 3 people (s3) | PRD adds a second competency (REQ-001: C1 and C2), REQ-022, NFR-005/007 | Unchanged sizing | Pitch scope says "one competency path" (conflicts with PRD's two) |
| Invariance "build small (4 categories)" (s2.8) | REQ-011 lists six categories | SLICE-011 five | n/a |

### 7. Rule 5 and rule 8
- Rule 5: only evidence on disk is the two contract scripts (reproduced by auditor). Every PRD acceptance criterion is testable, but Must items REQ-022, NFR-005, NFR-007 have no test. test-strategy s11 targets `delivery/G6-assurance/`, which does not exist (actual: `delivery/G6-assurance-audit/`).
- Rule 8: `dependency-register.md` missing although `validate_examples.py` already depends on `jsonschema` and ADR-0001 s6 lists ~12 libraries. No secrets found. threat-model T-12a: third-party PDFs/TXT in `delivery/G0-intake/` excluded only via local `.git/info/exclude`.
- Rule 6: hash canonicalisation decided in a contracts doc without an ADR (architecture Q8).

## Findings
| ID | Severity | Description | Owner | Due |
|---|---|---|---|---|
| F-01 | High | REQ-022, NFR-005, NFR-007 (Must) have no slice and no test; REQ-014..017, REQ-023, NFR-006 untested; plan s3/s11 and test-strategy s5 out of sync with PRD | principal-architect (plan), quality-engineer (tests) | Before G4 review (H6) |
| F-02 | High | Score-gate contradiction: test-strategy T-006a/XS-4 and plan REQ-006 say L1-L3; PRD, pitch, UX say all four; SharedEvidence requires `proficiency`; UX L4 has no pass outcome | product-owner (Founder confirms), then principal-architect, quality-engineer, ux-architect | Before SLICE-009 (H12); decision before G3 |
| F-03 | High | Threat model, implementation plan and test strategy assume ADR-0002 Option A while architecture baseline is Option B; no Founder decision recorded | Founder (ADR-0002); security-engineer to re-baseline TB4/TB7 | H6 |
| F-04 | High | Contract changes C1-C7 not applied; C2 means consent scope cannot be honoured (T-04c) | principal-architect / Dev 2 | Before G3 approval |
| F-05 | High | T-04a (Critical, learner authentication/IDOR) has no PRD NFR, slice or test; NFR-003 enforcement sits in cuttable SLICE-015 | product-owner, principal-architect | G4 |
| F-06 | Medium | REQ-007 Must and pitch headline keep mutation follow-ups against feasibility s2.4/s7.2; band lacks "illustrative, not calibrated" label | product-owner | G2 review |
| F-07 | Medium | Band depends on SLICE-010 (risk H) under the four-level rule; never-cut list excludes 009/010 | principal-architect | G4 |
| F-08 | Medium | G3 missing `dependency-register.md`, `quality-commands.json` empty; G4 CI pipeline absent | principal-architect, platform-engineer | G3/G4 |
| F-09 | Medium | G1 missing market-and-user-research.md and competitor comparison | research-analyst | G1 |
| F-10 | Low | Pitch "one competency path" vs PRD two competencies; invariance category counts 4/5/6 differ; perf thresholds 1 s/3 s/5 s differ | product-owner, quality-engineer | G2 review |
| F-11 | Low | Hash canonicalisation lacks ADR; UX traceability not keyed to REQ IDs; test-strategy G6 path wrong; state `profile: none` vs PRD A7 | principal-architect, ux-architect, quality-engineer, Chief of Staff | G3 review |

## Verdict
| Gate | Verdict | Blocking items |
|---|---|---|
| G1 | **FAIL** | Required artifact missing; no 3-alternative comparison; G0 not approved (F-09) |
| G2 | **CONDITIONAL** | Fix F-06, F-10; record Founder decision on score rule (F-02) and Q2 (two competencies); FINAL G1 needed for traceability. Owner: product-owner |
| G3 | **FAIL** | Dependency register missing, quality-commands unset, C1-C7 unapplied, threat model on wrong topology, Must items unmapped (F-03, F-04, F-05, F-08) |
| G4 | **FAIL** | Must requirements without slice/test, score-rule test contradicts PRD, no CI pipeline (F-01, F-02, F-07, F-08) |

## Recommendation to Founder
Decide three things first: (1) the score rule (all four levels, as PRD) and what an L4 "pass" is; (2) ADR-0002 Option B or A with a recorded rule-7 exception; (3) whether REQ-007 mutation follow-ups stay Must or become stubbed per feasibility. Then owners re-sync plan s3/s11, test-strategy s5, contracts (C1-C7) and the threat model before G3/G4 review.
