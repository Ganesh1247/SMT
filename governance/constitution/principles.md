# Engineering Principles

1. **Evidence over claims.** A working, tested behaviour outranks a document; a document outranks an assertion.
2. **Define before design, design before build.** Each stage consumes the approved output of the previous one.
3. **Separation of duties.** Authors never review their own work. Verification roles are independent of build roles.
4. **Smallest shippable slice.** Work is decomposed into vertical slices that deliver observable value and can be verified alone.
5. **Modular monolith by default.** One deployable unit, strict internal module boundaries, explicit contracts. Distribute only when an ADR proves the need.
6. **Decisions are recorded.** Any choice that is costly to reverse gets an ADR with alternatives and consequences.
7. **Security and accessibility are built in,** not audited in at the end. Threat model at G3; a11y in UX flows at G3.
8. **Reversibility.** Prefer changes that can be rolled back. Every release has a rollback plan.
9. **Honest status.** Report what works, what does not and what is simulated. Never present a mock as functional.
10. **Continuous improvement.** Every gate and release feeds metrics and lessons into `kaizen/`. Process changes need Founder approval.
11. **Least privilege.** Each agent has only the tools its role needs.
12. **Simplicity.** Choose the simplest design that meets the requirements; justify complexity.
