# Agent Context Graph

**Status:** Draft  
**Artifact class:** Semantic Graph / Engineering Artifact  
**Owner:** Architecture Owner  
**Required reviewers:** Engineering Owner, Architecture Owner  
**Authority:** Proposed baseline; not authoritative until approved under the document lifecycle  
**Generator baseline:** `populate-artifact-system.py` v1.0.0

## Purpose

This artifact defines the core contract; it also defines how task-relevant knowledge is selected, minimized, ordered, bounded, and proven current; and defines bounded machine actor identity, authority, task scope, context, provenance, escalation, and review. It exists within Monad's semantic graph concern, which covers the graph representation of engineering entities and relationships that allows Monad to answer why, impact, ownership, provenance, dependency, and coverage questions. The document turns that concern into an explicit, reviewable engineering contract rather than leaving it in chat history, tribal knowledge, tool defaults, or implementation accidents.

## Scope

In scope are the semantics, responsibilities, evidence, lifecycle, and interfaces directly needed to make **Agent Context Graph** dependable. The primary quality concerns are ontology, identity, edges, invariants, query.

Out of scope are unrelated implementation choices, vendor-specific behavior that does not affect the contract, and authority that belongs to a higher-level vision, governance, accepted ADR, or approved specification. This artifact may constrain implementation but must not silently expand project scope.

## Governing principles

- Agent Context Graph has an explicit scope and must not silently absorb neighboring responsibilities.
- Every normative claim must be testable, reviewable, or linked to evidence that can be independently inspected.
- Stable identifiers are never reused for semantically different concepts or records.
- Changes that alter public behavior, compatibility, authority, security posture, or accepted risk require impact analysis before approval.
- Generated projections may summarize or index this artifact but may not silently redefine its meaning.
- Agents cannot expand their own authority, approve their own high-consequence work, or treat model confidence as authorization.
- Task context and produced changes retain enough provenance to reconstruct the instructions, governing artifacts, and validation used.
- Graph identity must remain stable across traversal order and serialization order.
- Every derived edge retains provenance sufficient to explain why the relationship exists.
- Graph queries must distinguish absence of evidence from evidence of absence.

## Required inputs

- the current approved product and architecture intent relevant to this concern;
- applicable accepted ADRs and approved specifications;
- known security, privacy, reliability, performance, and operational constraints;
- stable identifiers for governed entities and related artifacts;
- evidence from implementation, tests, research, incidents, or prior reviews when available;
- explicit assumptions wherever evidence is incomplete.

## AI and agent boundary

The artifact defines which information may enter model context, which actions an agent may propose or perform, and which decisions remain human-only.

Provider-specific capabilities are isolated behind model-independent contracts where practical.

Prompts, context selection, tool use, and generated changes are treated as engineering inputs with provenance rather than invisible implementation detail.

## Interfaces and traceability

This artifact participates in Monad's end-to-end traceability chain. It should link upward to the vision, requirement, decision, risk, or policy that justifies it and downward to the specifications, work packets, implementation, tests, generated artifacts, releases, or operational evidence that realize or verify it. Those links are semantic relationships, not decorative references.

When another artifact depends on this contract, the dependency should be machine-discoverable through stable identifiers or resolvable repository references. A change to this artifact must therefore include impact analysis for known consumers and must regenerate the machine-readable knowledge projection.

## Failure and exception handling

A violation of this contract is represented explicitly. Invalid input, denied authority, incompatible version, missing evidence, transient dependency failure, permanent failure, and unknown outcome are not collapsed into a generic success/failure flag when they require different recovery or governance.

Exceptions are narrow, owned, justified by evidence, time- or trigger-bounded where practical, and recorded with the residual risk they introduce. An exception cannot silently redefine the underlying rule.

## Lifecycle and change control

1. **Draft:** authorship and evidence collection; not relied upon as approved authority.
2. **Review:** scope and semantics are stable enough for designated reviewers to evaluate.
3. **Approved:** the accountable authority accepts the contract within its stated scope.
4. **Implemented:** delivered behavior and evidence conform where implementation status is meaningful.
5. **Deprecated/Superseded/Retired:** transition is explicit, dependencies are migrated, and history is preserved.

Meaning-changing updates identify affected consumers, compatibility impact, migration needs, risk change, and verification changes. Accepted historical meaning is superseded rather than rewritten without trace.

## Verification

- Verify that the document's scope and terminology agree with higher-authority artifacts.
- Verify that every mandatory rule has an observable conformance or review method.
- Verify success, boundary, invalid, unauthorized, interrupted, and recovery behavior where applicable.
- Verify compatibility and migration behavior for any externally consumed representation or protocol.
- Verify security and privacy properties at every trust or data boundary introduced by this artifact.
- Verify generated machine companions are synchronized with the canonical source.
- Record evidence links in the implementing work packet, review, or release record.

## Acceptance criteria

- [ ] Purpose, scope, exclusions, and owner are explicit.
- [ ] Terminology is consistent with `governance/terminology.md` or intentionally narrows it.
- [ ] Governing decisions, requirements, risks, and dependent artifacts are linked.
- [ ] Normative statements are testable or have a defined manual evidence path.
- [ ] Compatibility, security, failure, and recovery concerns are addressed where applicable.
- [ ] Reviewers can distinguish current evidence from assumptions and proposals.
- [ ] Machine-readable projections regenerate without drift.
- [ ] Approval, if granted, records authority, date, scope, conditions, and dissent.

## Review trigger

Review this artifact when a governing requirement or ADR changes, an implementation or incident contradicts an assumption, compatibility or security impact changes, ownership changes, or a dependent artifact cannot be implemented or verified without reinterpretation.

## Canonicality

`artifact-system/semantic-graph-planning/agent-context-graph.md` is the human-readable canonical source for this artifact once approved. Any representation under `machine/` is a deterministic derivative and must not be edited independently.
