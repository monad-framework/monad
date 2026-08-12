# Product and Engineering Principles

**Status:** Proposed stabilization baseline

1. **Knowledge before automation.** Monad must understand the engineering meaning and authority of work before automating consequential action.
2. **Canonical source, deterministic projections.** Generated graph, indexes, docs, dashboards, and AI context retain source provenance and can be regenerated.
3. **Local first.** The core loop works from the repository and local toolchain; cloud services extend rather than own the product.
4. **Deterministic core, probabilistic assistance.** LLM reasoning sits above or beside deterministic parsing, identity, graph construction, validation, and execution planning.
5. **Human authority is explicit.** Automation can enforce or propose but cannot silently invent approval.
6. **Explain every consequential result.** Diagnostics, graph edges, policy findings, execution decisions, and context selection should be traceable to inputs/rules.
7. **Stable identity over filenames.** Engineering entities need identities and provenance resilient enough for meaningful history and semantic diff.
8. **Native tools remain native.** Integrate through adapters and capability contracts rather than replacing mature ecosystems without compelling evidence.
9. **Incrementality follows semantics.** Re-run work because relevant semantic state changed, not simply because some file timestamp changed.
10. **Fail closed on authority, fail clearly on knowledge.** Missing permission/authority blocks consequential action; unsupported/ambiguous knowledge produces visible diagnostics.
11. **Security and privacy are structural.** Context minimization, secret boundaries, plugin/agent permissions, supply-chain provenance, and safe execution are architecture concerns.
12. **Modularize early, split late.** Maintain clean boundaries in one repository until independent lifecycle/distribution/ownership justifies separation.
13. **Dogfood with evidence.** Monad should increasingly build Monad, but self-hosting claims require deterministic proof rather than symbolism.
14. **Optimize the whole engineering loop.** A faster command is not success if it increases ambiguity, rework, risk, or maintenance elsewhere.
15. **Preserve history, supersede meaning.** Decisions and contracts evolve through explicit lifecycle rather than silent rewriting.