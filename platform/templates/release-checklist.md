<!-- STATUS: TEMPLATE -->
# Release Checklist

Owner: <role> | Gate: <Gn> | Version: 0.1 | Date: <YYYY-MM-DD> | Reviewer: <independent role>
Inputs: <paths of upstream FINAL artifacts>

## Preconditions
- [ ] G6 approved - [ ] no open Critical/High findings - [ ] CI green on release commit

## Build and versioning
- [ ] version/tag - [ ] changelog - [ ] reproducible artefacts

## Data and config
- [ ] migrations tested forward and back - [ ] environment variables set - [ ] no secrets in repo

## Rollback
_Trigger conditions, steps, owner, rehearsal result._

## Observability
- [ ] health check - [ ] metrics - [ ] alerts - [ ] dashboards show data

## Documentation
- [ ] release notes - [ ] runbook current

## Go / no-go
_Founder decision, date._
