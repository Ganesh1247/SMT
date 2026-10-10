<!-- STATUS: TEMPLATE -->
# Architecture Overview

Owner: <role> | Gate: <Gn> | Version: 0.1 | Date: <YYYY-MM-DD> | Reviewer: <independent role>
Inputs: <paths of upstream FINAL artifacts>

## Context and quality attributes
_System context; ranked quality attributes with targets._

## Module map (bounded contexts)
_Module | Responsibility | Owner | Public api surface | Depends on (api only) | Data owned._

## Layering and dependency rules
_domain / application / infrastructure / api; enforcement via architecture tests._

## Data model
_Entities per module, ownership, consistency approach._

## Integration contracts
_Internal events, external APIs, versioning._

## Deployment topology
_Single deployable unit; environments; scaling approach._

## Technology choices
_Link each to its ADR._

## Cross-cutting concerns
_Auth, logging, config, error handling, observability._

## Requirement coverage
_REQ-ID -> module -> slice._

## Risks and fallbacks
_TBD_
