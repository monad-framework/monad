<!-- artifact-catalog-baseline:v1 -->
# Generated Artifact Policy

**Catalog path:** `artifact-system/repo-artifact-governance/GENERATED-ARTIFACT-POLICY.md`  
**Status:** Draft  
**Artifact class:** policy  
**Owner:** Engineering Owner  
**Authority:** Describes an artifact contract; it is not automatically an instantiated or accepted project record.

## Purpose

The **Generated Artifact Policy** artifact makes generated artifact policy explicit and reviewable within Monad. It exists to prevent important repo artifact governance decisions from living only in chat, memory, implementation detail, or tool-specific state.

Within the artifact catalog this document defines mandatory rules, permitted exceptions, authority, enforcement, and review triggers. Its family focuses on repository authority, contribution, branching, reviews, generated artifacts, compatibility, human/agent control, and change policy. The contract is deliberately independent of a particular implementation tool so humans, ChatGPT, Codex, CI, and future Monad automation can reason about the same engineering intent.

## Activation

Create or promote an instantiated Generated Artifact Policy when an accepted decision, approved specification, active Work Packet, release gate, recurring operational need, or material risk requires a durable representation. Do not activate the artifact merely because the catalog contains this contract.

Before activation, identify the accountable owner, canonical repository location, stable identifier scheme, required reviewers, update triggers, and the validation that proves the artifact is current. If a simpler existing artifact can carry the same meaning without ambiguity, prefer reuse over duplication.

## Scope

This contract governs the structure, semantics, authority, lifecycle, traceability, and verification of Generated Artifact Policy records used by Monad. It does not grant decision authority, approve an implementation, or supersede higher-order governance. Tool-specific UI fields are projections unless explicitly designated canonical.

Out of scope are informal brainstorming, transient chat, generated summaries without canonical provenance, and implementation details that do not affect the contract represented by this artifact.

## Required content

An instantiated artifact MUST make the following reviewable:

- stable identity, status, owner, scope, and review/activation state.
- the problem or decision pressure that caused the artifact to exist.
- explicit in-scope and out-of-scope boundaries.
- links to governing requirements, decisions, specifications, risks, work, and evidence.
- assumptions and unresolved questions that could change the result.
- normative rules using testable language.
- exception authority and expiry.
- enforcement and audit mechanism.

Unknown information MUST be labeled as unknown, assumption, proposal, or deferred work rather than fabricated to make the record appear complete.

## Normative rules

1. The canonical artifact MUST identify its status and owner when reliance on it affects engineering action.
2. Meaning-changing edits MUST preserve history through version control and, for Approved material, follow the applicable change-control or supersession process.
3. The artifact MUST NOT silently contradict a higher-authority accepted decision, approved specification, or legal/security obligation.
4. Claims used to authorize consequential work MUST link to evidence or clearly state the evidence gap.
5. Stable identifiers MUST NOT be reused for a different meaning after publication.
6. Machine-generated projections MUST retain canonical source identity and MUST NOT become a competing editable source of truth.
7. Automation MAY validate, index, summarize, or project the artifact, but approval remains with the accountable human authority unless governance explicitly delegates a bounded mechanical decision.

## Relationships and traceability

At minimum, record upstream authority and downstream consumers that materially depend on this artifact. Prefer typed relationships such as `governed-by`, `implements`, `specified-by`, `depends-on`, `verifies`, `blocks`, `supersedes`, `generated-from`, or `evidenced-by` rather than untyped prose references.

When the Monad semantic graph supports this artifact class, its stable identity and relationships SHOULD be machine-queryable. A reviewer should be able to move from product intent to this artifact and from this artifact to authorized work, implementation evidence, and release disposition without reconstructing history from conversation.

## Lifecycle

The default lifecycle is **Draft -> Review -> Approved -> Implemented**, followed when necessary by **Deprecated**, **Superseded**, or **Retired**. Not every artifact needs every state; the instantiated contract must state deviations.

Drafts may change freely within branch review. Approval records who accepted the artifact and its effective scope. Implemented means required behavior or controls are demonstrably present, not merely that a document was merged. Superseded and retired records remain discoverable for historical provenance.

## Security, privacy, and agent use

Store no secret, credential, private key, unnecessary personal data, or restricted operational payload merely to make the artifact self-contained. Reference controlled evidence when detail belongs elsewhere. Security-sensitive exceptions and authority changes require explicit review.

AI agents may use this artifact for context only when they can identify the canonical source and status. An agent MUST distinguish Draft guidance from Approved authority, MUST surface contradictions instead of choosing silently, and MUST keep generated recommendations separate from human approval.

## Verification

Verification for an instantiated Generated Artifact Policy includes:

- structural validation of required metadata and sections;
- link/identifier integrity and relationship resolution;
- consistency with governing decisions and specifications;
- evidence that required reviewers and approvals are present;
- checks that generated machine companions match canonical source; and
- domain-specific conformance tests where the artifact defines executable behavior.

A review passes only when omissions are either resolved or explicitly accepted by an authority permitted to accept the residual risk.

## MVP relevance

For MVP Release 1, activate this artifact only if it directly supports the core loop `canonical engineering knowledge -> semantic compilation -> graph/query/explain -> bounded agent context -> deterministic validation`, or if it retires a release-blocking correctness, security, operability, compatibility, or governance risk. Otherwise this Draft contract remains part of the long-term catalog.

## Evolution

Refine this baseline with evidence from actual use. Once manually specialized and reviewed, remove `<!-- artifact-catalog-baseline:v1 -->` so the catalog population tool no longer owns the file. Major semantic changes to an Approved contract require impact analysis across its instantiated artifacts and machine schema/projection behavior.
