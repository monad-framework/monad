# WP-MVP-0006 — Local reference resolution

**Status:** READY_TO_AUTHORIZE — gated only by formal closure/canonical integration of WP-MVP-0005; **NOT AUTHORIZED / NOT STARTED**  
**Owner:** Monad Core  
**Epic:** EPIC-003  
**Feature:** F-003-04  
**Program Increment:** PI-MVP-001  
**Work Cycle:** WC-MVP-0002  
**Product Goal:** PG-001

> Readiness is planning state only. It does not authorize EOSE execution, create an execution record, change EOS lifecycle state, or permit implementation before the Work Packet is separately authorized.

## Objective

Resolve parser-emitted local governed identifiers and Markdown/file references deterministically against the complete canonical parsed-source index, producing provenance-rich typed relation candidates while preserving missing, ambiguous, external, noncanonical, and invalid references explicitly and without network access, target filesystem dereference, repository execution, or semantic inference.

## Governing authority

- `FR-001`, `FR-002`, `FR-003`, `FR-004`; `QR-001`, `QR-003`
- `ADR-0002` — Canonical Repository Root and Configuration
- `ADR-0003` — Stable Source and Document Identity
- `ADR-0004` — Safe Deterministic Canonical Ingestion Boundary
- `ADR-0005` — MVP Core Implementation Topology — **Accepted**
- `IFC-WORKSPACE-0001`
- `DATA-SOURCE-0001`
- `TECH-WORKSPACE-0001`
- `TECH-INGEST-0001`
- `TECH-INGEST-0002`
- `TECH-INGEST-0003`
- `testing/strategy.md`
- `testing/quality-gates.md`

## Readiness/start gate

The packet is semantically and operationally refined enough to authorize immediately when the following predecessor condition is true:

1. `WP-MVP-0005` is formally CLOSED under its owning workstream;
2. its accepted structured-configuration implementation is canonical on `main` (including the implementation currently proposed by PR #488 or its formally accepted successor);
3. the resulting `main` revision passes the predecessor's required integration gates; and
4. `WC-MVP-0002` still permits the next child Work Packet under its one-at-a-time WIP rule.

No additional product/architecture decision is currently required to authorize WP-MVP-0006 after that gate.

## Corrected dependency model

The old packet summary incorrectly said WP-MVP-0004 and WP-MVP-0005 both provide parsed reference candidates. The actual handoff is:

- `WP-MVP-0002` provides deterministic canonical discovery and the configured-source set;
- `WP-MVP-0003` provides `SourceRecord`, `DocumentIdentity`, governed identifier identity, duplicate-ID diagnostics, and exact-byte provenance;
- `WP-MVP-0004` is CLOSED and provides `ParsedMarkdownDocument`, `LinkCandidate`, `IdentifierReferenceCandidate`, source ranges, document identity, and parser diagnostics;
- `WP-MVP-0005`, after formal closure, provides the provenance-bound semantic `monad.toml` document and the same effective configuration semantics that governed discovery; it is used to keep canonical/noncanonical classification aligned with the actual run and is **not** treated as a second Markdown reference-candidate producer;
- the complete parsed target index MUST exist before resolution; resolver logic MUST NOT discover a winner by filesystem traversal.

## Exact intended scope

### 1. Reference input syntax

WP-MVP-0006 resolves candidates already emitted by approved parsers. It MUST NOT rescan Markdown prose to invent references.

MVP input classes are:

1. `IdentifierReferenceCandidate` — a parser-recognized governed identifier token with source range;
2. `LinkCandidate` — an inline Markdown link destination with label and source range;
3. same-document fragment references such as `#section`, represented through `LinkCandidate`;
4. file-plus-fragment references such as `other.md#section`;
5. URI-scheme or protocol-relative external references, represented as external records and never dereferenced.

Reference-style Markdown links, renderer-specific MDX semantics, arbitrary HTML navigation semantics, natural-language references, package/module specifiers, and remote includes are not added by this packet unless an upstream parser already emits a governed candidate under an approved contract.

### 2. Governed identifier namespaces

`GovernedIdentifier { namespace, value }` remains the authoritative identifier shape from stable identity work.

Resolution rules:

- namespace is the governed identifier family supplied by parsing/identity;
- lookup key is exact `(namespace, value)`;
- identifier value remains case-sensitive and is not normalized through case folding;
- no prefix guessing, fuzzy matching, alias expansion, filename fallback, or cross-namespace fallback is allowed;
- one exact target resolves;
- zero exact targets is `unresolved`;
- more than one exact target is `ambiguous` and all candidates are retained in deterministic order.

Preflight found that the landed Markdown parser's identifier allowlist does not cover every canonical identifier family currently present in the configured corpus (notably `IFC`, and canonical legacy `MKE` material). Task #496 owns the bounded parser/resolver handoff correction. That correction does not reopen WP-MVP-0004 lifecycle state and does not authorize work by itself.

### 3. Source and target identity

Every resolver output retains the referring source/document identity from `DATA-SOURCE-0001` and `ADR-0003`:

- referring `DocumentId`;
- referring `SourceId`;
- referring canonical repository-relative path;
- parser-supplied source range;
- source content/parser provenance already present on `SourceRecord`.

A resolved target carries its authoritative target `DocumentId`, `SourceId`, canonical path, and source-kind/document provenance. An unresolved/external/noncanonical/invalid target MUST NOT receive a fabricated target identity.

For ambiguous resolution, all candidate target identities are retained in canonical order.

### 4. Reference index

Expected in-memory index shape in `monad-core`:

```text
ReferenceIndex
  by_governed_identifier: BTreeMap<GovernedIdentifier, Vec<ReferenceTarget>>
  by_canonical_path:      BTreeMap<String, Vec<ReferenceTarget>>
  casefold_paths:         BTreeMap<String, Vec<String>>   # diagnostic aid only
  canonicality_policy:    effective artifact include/exclude context
```

`ReferenceTarget` is expected to retain document/source identity and canonical path without retaining or reading target content during resolution.

Index construction MUST be independent of caller/input order. Duplicate governed IDs are represented as multiple target identities; no insertion order may choose a winner.

The root `monad.toml` semantic document is a canonical target even though it is established by the workspace/configuration contract rather than ordinary artifact-root glob discovery.

### 5. Resolution precedence

There is no cross-class fallback.

For an `IdentifierReferenceCandidate`:

1. exact governed namespace + identifier lookup;
2. one target => `resolved`;
3. none => `unresolved`;
4. multiple => `ambiguous`.

For a `LinkCandidate`:

1. classify the destination as unsafe/rooted, external, fragment-only, or local path;
2. unsafe/root-escaping local reference => `invalid`;
3. external URI => `external` without dereference;
4. fragment-only => target the referring document and preserve fragment opaquely;
5. local path => lexical repository normalization, then exact canonical-path lookup;
6. one exact canonical target => `resolved`;
7. multiple exact canonical targets => `ambiguous`;
8. no target but path is canonical-eligible under the effective run configuration => `unresolved`;
9. excluded/out-of-scope/derived path => `noncanonical`.

An unresolved governed ID MUST NOT fall back to path lookup. An unresolved path MUST NOT fall back to basename, governed-ID, extension, case-folded, or traversal-order lookup.

### 6. Relative and canonical paths

Markdown file references are resolved lexically from the referring source's canonical parent directory.

Rules:

- `/` is the canonical separator;
- `.` segments are normalized away;
- parent-relative `..` segments are normalized lexically only while the result remains inside the selected repository root;
- a `..` operation that would traverse above repository root is `invalid` and produces a root-escape diagnostic;
- rooted POSIX paths, Windows drive/root forms, backslash-based host-path forms, and other host-absolute references are not treated as repository references;
- normalization never calls host filesystem canonicalization and never dereferences symlinks;
- successful normalized keys contain no leading slash, `.` segment, or `..` segment;
- no URL decoding, extension guessing, basename search, or platform-dependent path repair is performed.

The canonical path is an output lookup key, not a new Markdown root-relative syntax. No separate `/repo/path` link syntax is invented in MVP.

### 7. Fragments/anchors

Same-document anchors are in scope only at document-reference/provenance level.

- `#fragment` resolves to the referring document;
- `path.md#fragment` resolves `path.md` and retains the fragment;
- fragment text is preserved opaquely;
- WP-MVP-0006 MUST NOT claim a renderer-specific heading slug/anchor exists because no canonical anchor-slug contract currently governs that behavior;
- absence or validity of a rendered fragment is therefore not a resolver failure in MVP.

### 8. External references

A URI-scheme or protocol-relative destination is `external`.

- it is preserved as a typed external reference record;
- it is never fetched;
- `file:` or another scheme does not grant filesystem access;
- external content cannot establish canonical semantic truth during this phase.

### 9. Canonical versus noncanonical targets

Canonicality is determined from the same effective configuration/discovery context that selected the run's semantic inputs, plus the canonical root `monad.toml` document.

The resolver MUST NOT stat/read a target to decide whether it exists.

- exact path already present in the parsed canonical index => canonical target candidate;
- normalized path selected by effective include policy but absent from the complete parsed index => `unresolved`/missing canonical target;
- excluded path, generated/control path, or path outside configured canonical artifact selection => `noncanonical`;
- `.eos/`, `machine/`, `.monad/manifest.yaml`, build output, VCS internals, and other non-authoritative/derived material cannot be promoted by being named in a link.

A successful path resolution establishes target identity, not the semantic authority of every statement inside the target. Authority/status validation remains downstream.

### 10. Resolution states

The resolver contract includes at least:

```text
resolved
unresolved
ambiguous
external
noncanonical
invalid
```

Semantics:

- `resolved` — exactly one authoritative target identity;
- `unresolved` — canonical-eligible local/ID target is absent; absence is not rewritten as a negative semantic claim;
- `ambiguous` — more than one authoritative target candidate; all candidates retained; no winner selected;
- `external` — remote/schemed reference retained without dereference;
- `noncanonical` — target key is outside canonical semantic input for the run;
- `invalid` — syntactically or containment-unsafe reference cannot be resolved safely.

Whether `unresolved`, `external`, or `noncanonical` is an artifact-contract error is deliberately deferred to later semantic validation. Resolver state is not itself policy verdict.

### 11. Malformed identifiers

Malformed explicit governed identifiers remain the parser's responsibility under `TECH-INGEST-0001`.

WP-MVP-0006:

- consumes only valid `IdentifierReferenceCandidate` values;
- does not reinterpret a malformed token as a valid identifier;
- preserves upstream parser diagnostics;
- excludes malformed target identifiers from the governed-ID target index;
- does not rescan raw prose to manufacture missing candidates.

Namespace/parser coverage conformance is explicitly verified under Task #496 and #501.

### 12. Self-reference and cycles

Self-reference is not a resolution error.

- an ID or file reference that resolves to its own document is `resolved`;
- a fragment-only reference is a resolved same-document reference;
- A→B→A and larger cycles do not trigger recursive resolution and therefore cannot cause resolver recursion/infinite traversal;
- whether a particular semantic relationship cycle is allowed is graph/validation work downstream.

### 13. Symlinks and special files

WP-MVP-0006 performs no target filesystem I/O.

- symlink containment/alias/cycle handling remains a discovery responsibility;
- only identities/index entries admitted by discovery/parsing can become canonical targets;
- a reference cannot cause symlink dereference;
- a FIFO/socket/device/special path cannot be opened by the resolver;
- platform-gated negative tests MUST prove resolver behavior does not require target `stat`, read, open, or canonicalization.

### 14. Case sensitivity and platform determinism

- canonical identity/path matching is case-sensitive;
- a case-folded near match is diagnostic context only and MUST NOT resolve;
- one case-insensitive near match may produce a deterministic case-mismatch diagnostic;
- multiple case-insensitive near matches may produce deterministic ambiguity/collision context;
- discovery's existing `CaseCollisionRisk` evidence remains authoritative for discovered-path collision risk;
- resolver ordering uses canonical UTF-8/string ordering and must not depend on host filesystem case behavior.

### 15. Duplicate candidates

Occurrence provenance is preserved.

- distinct source ranges remain distinct candidates even when they normalize to the same target;
- distinct syntactic reference kinds remain distinct candidates even when they resolve to the same target;
- an exact duplicate input with identical referring identity, source range, kind/rule, raw reference, and normalized target MAY be coalesced deterministically;
- graph-level duplicate-edge semantics are not decided here.

## Typed relation-candidate contract

The intended MVP `monad-core` model is equivalent to:

```text
ReferenceKind
  GovernedIdentifier
  MarkdownFile
  SameDocumentFragment
  ExternalUri

ReferenceTargetKey
  GovernedIdentifier { namespace, value }
  CanonicalPath { path }
  ExternalUri { value }
  Invalid { raw }

ResolutionState
  Resolved | Unresolved | Ambiguous | External | Noncanonical | Invalid

ReferenceOrigin
  document_id
  source_id
  canonical_path
  source_range

ReferenceTarget
  document_id
  source_id
  canonical_path

RelationCandidate
  origin
  raw_reference
  reference_kind
  rule_id
  normalized_target_key
  fragment?
  resolution_state
  targets[]

ReferenceResolution
  candidates[]
  diagnostics[]
```

Implementation is expected in a bounded `crates/monad-core/src/reference.rs` (or equivalently named single resolver module) exported from `monad-core`; no new crate is justified by ADR-0005 for this packet.

A suitable API shape is:

```text
build_reference_index(parsed_documents, configuration_document,
                      discovery, effective_configuration)
    -> ReferenceIndexResult

resolve_references(index, parsed_markdown_documents)
    -> ReferenceResolution
```

The exact Rust borrowing/container signatures may vary without changing semantics. Semantic behavior MUST remain in `monad-core`, not CLI presentation code.

### Relation rule provenance

`rule_id` identifies the deterministic syntactic resolver rule that produced the candidate. MVP rules must distinguish at least:

- governed identifier reference;
- Markdown local file reference;
- same-document fragment reference;
- external URI reference.

These are resolver rule/reference hints, **not** final semantic graph edge types. WP-MVP-0007 remains authoritative for graph ontology.

## Diagnostics conventions

WP-MVP-0011 later defines the product-wide diagnostic contract. WP-MVP-0006 therefore defines only a bounded resolver diagnostic enum/record and MUST NOT prematurely promise the final public diagnostic schema.

Resolver diagnostics need deterministic codes for at least:

- invalid/rooted local reference;
- repository root escape;
- case mismatch/case-collision context;
- ambiguous target at a reference occurrence.

Missing targets, external references, and noncanonical references are first-class resolution states and are not automatically fatal diagnostics.

Diagnostics retain referring identity/path/source range and normalized target context where available. They use repository-relative paths and MUST NOT leak unrelated absolute clone/host paths.

## Deterministic ordering and serialization

Candidate ordering is canonical by:

1. referring `DocumentId`;
2. source-range `byte_start`, `byte_end`, `line_start`, `line_end`;
3. resolver rule/reference-kind key;
4. normalized target key;
5. raw reference text;
6. fragment;
7. resolution state;
8. ordered target identities.

Ambiguous target lists are ordered by target `DocumentId`, then canonical path/source identity as deterministic tie-breakers.

Diagnostics are ordered by referring identity, source range/location, diagnostic code, normalized target context, and deterministic message/context fields.

Equivalent inputs in different parser/document/index order MUST serialize to byte/structure-equivalent canonical output where the resolver declares canonical serialization.

No canonical resolver output may depend on:

- filesystem enumeration order;
- absolute clone path;
- inode/device values;
- wall-clock time;
- random identifiers;
- hash-map insertion order;
- network state;
- ungoverned model/LLM output.

## Acceptance criteria

### US-018 — Local artifact resolution

- [ ] exact governed-ID references resolve by exact namespace + value against the complete target index;
- [ ] source-relative local file references normalize lexically and resolve only to exact canonical parsed targets;
- [ ] safe parent-relative `..` resolution remains inside repository root; root escape is rejected;
- [ ] same-document and file-plus-fragment references preserve fragment provenance without renderer-specific anchor claims;
- [ ] `monad.toml` can be represented as the canonical structured-configuration target;
- [ ] no basename, case-folded, extension, traversal-order, or semantic-inference fallback exists;
- [ ] self-reference and cycles resolve without recursion.

### US-019 — Unresolved refs

- [ ] missing canonical/ID targets remain explicitly `unresolved`;
- [ ] duplicate target IDs/multi-target lookups remain `ambiguous` with every candidate retained;
- [ ] external references remain explicitly `external` and are never fetched;
- [ ] excluded/out-of-scope/derived targets remain explicitly `noncanonical` and are never promoted;
- [ ] containment-unsafe/malformed local references remain explicitly `invalid` with source-located diagnostics;
- [ ] case mismatch never becomes case-folded success;
- [ ] absence is not rewritten into a negative semantic claim or policy verdict.

### US-020 — Typed relation candidates

- [ ] every candidate carries referring identity, source range, raw reference, normalized target key, rule/reference kind, state, and applicable target identity/provenance;
- [ ] ambiguous candidates preserve all target identities deterministically;
- [ ] exact duplicate inputs may be coalesced only under the declared identity/range/kind/raw-target rule; distinct occurrences remain distinct;
- [ ] relation hints do not preempt graph ontology;
- [ ] ordering/serialization is deterministic under randomized input ordering and equivalent clean-clone inputs.

### Security/trust boundary

- [ ] resolution performs no network request;
- [ ] resolution performs no target file `stat`/open/read/canonicalization or symlink dereference;
- [ ] resolution executes no repository script, code, macro, command substitution, package manager, plugin, include, or native tool;
- [ ] environment state does not alter semantic resolution;
- [ ] rooted/root-escaping paths cannot leave the selected Monad root;
- [ ] noncanonical/control/generated material cannot become canonical merely because it is referenced.

## Task decomposition

The formal Tasks are planned but remain **NOT AUTHORIZED / NOT STARTED**:

1. **#496 — US-018: Reconcile reference inputs and governed identifier namespaces**  
   Lock the parser→resolver contract, reconcile active governed namespace coverage, preserve malformed-ID parser diagnostics, and version any required parser-contract correction.

2. **#497 — US-018: Build deterministic reference index and canonicality classifier**  
   Build exact ID/path indices, case diagnostic index, `monad.toml` target integration, and pure effective-config canonicality classification without target filesystem probing.

3. **#498 — US-018: Resolve governed IDs, local files, fragments, and external URLs**  
   Implement exact lookup/classification, safe lexical path normalization, external preservation, fragment handling, self/cycle behavior, and no fallback semantics.

4. **#499 — US-019: Preserve unresolved, ambiguous, noncanonical, and invalid reference states**  
   Implement explicit state semantics, ambiguous candidate retention, root-escape/unsafe diagnostics, case diagnostics, and no negative-claim rewriting.

5. **#500 — US-020: Emit typed provenance-rich relation candidates deterministically**  
   Implement the output model, syntactic rule provenance, duplicate-occurrence rules, canonical ordering, and deterministic serialization.

6. **#501 — US-020: Build reference-resolution conformance corpus and acceptance evidence**  
   Prove all positive, negative, boundary, randomized-order, security, integration, Unicode, clone-equivalence, symlink/special-file, and noncanonical-material cases.

## Fixture/test matrix

| Fixture / property | Expected result | Story/Task |
| --- | --- | --- |
| exact `ADR-0003` / `TECH-INGEST-0003` ID | resolved exact target | US-018 / #496–498 |
| active `IFC-*` / canonical `MKE-*` namespace coverage | parser/index handoff represents identifier consistently | US-018 / #496 |
| missing governed ID | unresolved, no fabricated target | US-019 / #499 |
| duplicate governed ID in two documents | ambiguous; both targets sorted; identity diagnostic preserved | US-019 / #497/#499 |
| relative `peer.md` | normalized from referring parent, exact path resolve | US-018 / #498 |
| `./peer.md` | `.` removed, same result as `peer.md` | US-018 / #498 |
| safe `../peer.md` remaining inside root | normalized and eligible for exact resolution | US-018 / #498 |
| `../../...` escaping root | invalid + root-escape diagnostic | US-019 / #499 |
| rooted `/etc/passwd` / drive-root form | invalid; never host-resolved | US-019 / #499 |
| backslash host path | invalid/unsupported local form; never host-resolved | US-019 / #499 |
| `#section` | resolved to referring document; opaque fragment retained | US-018/020 / #498/#500 |
| `peer.md#section` | file resolves; opaque fragment retained | US-018/020 / #498/#500 |
| nonexistent path that is canonical-eligible | unresolved | US-019 / #497/#499 |
| excluded/out-of-artifact-root path | noncanonical | US-019 / #497/#499 |
| `.eos/*`, `machine/*`, build outputs | noncanonical; no promotion | US-019 / #497/#501 |
| `.monad/manifest.yaml` | noncanonical legacy material; no configuration authority | US-019 / #497/#501 |
| root `monad.toml` | canonical configuration target | US-018 / #497 |
| `https://...`, `mailto:...`, `//host/...` | external; zero fetch | US-019 / #498/#501 |
| `file:...` | external/schemed record; zero filesystem dereference | US-019 / #498/#501 |
| duplicate filenames in separate directories | exact lexical path only; no basename ambiguity/winner | US-018 / #498 |
| exact-case path | resolves | US-018 / #497/#498 |
| wrong-case near match | no resolve; deterministic case diagnostic context | US-019 / #499 |
| two case-folded near matches | no folded winner; deterministic collision/ambiguity context | US-019 / #499 |
| malformed explicit governed ID | parser diagnostic retained; absent from authoritative ID index | US-019 / #496/#501 |
| same target referenced at two source ranges | two provenance-bearing candidates | US-020 / #500 |
| exact duplicate candidate object | deterministic coalescing permitted | US-020 / #500 |
| self-reference | resolved self target | US-018 / #498 |
| A→B→A cycle | both candidates resolve; no recursive traversal | US-018 / #498 |
| Unicode canonical paths/reference text | stable exact resolution/order | US-020 / #500/#501 |
| shuffled document/candidate/index input | identical canonical output | US-020 / #500/#501 |
| equivalent clean clones | identical identities/resolution output | US-020 / #501 |
| symlink/external/cyclic target scenarios | resolver does not dereference; discovery boundary governs eligibility | Security / #501 |
| FIFO/socket/device/special target path | resolver performs no stat/open/read and cannot hang on target | Security / #501 |

## Test strategy

### Unit tests

- target-key classification;
- lexical path normalization/containment;
- exact ID/path lookup;
- resolution-state transitions;
- case diagnostic behavior;
- duplicate candidate handling;
- target ordering and candidate serialization.

### Property tests

- permutation invariance for documents, candidates, target vectors, and discovery provenance;
- normalized safe path never contains leading slash, `.` or `..` segments;
- root-escape input never yields a resolved target;
- no ambiguous lookup produces a single traversal-order-selected target;
- equivalent indexed identities produce equivalent relation output.

### Contract/integration tests

- actual WP-MVP-0004 Markdown parser output → resolver;
- post-WP-MVP-0005 semantic configuration/effective configuration + discovery → canonicality classifier/index;
- `monad.toml` canonical-target behavior;
- duplicate identifier diagnostics from identity work carried into ambiguous resolution;
- source ranges/provenance retained end to end.

### Negative/security tests

- no network transport is reachable from resolver path;
- no repository command/process execution;
- no target filesystem read/stat/canonicalization/symlink dereference;
- external/`file:`/command-looking destinations remain inert;
- root escapes and host-rooted paths fail closed;
- control/generated/noncanonical paths are never promoted.

### Acceptance evidence

Later authorized execution must record:

- exact source revision and predecessor revision;
- parser/config/resolver contract versions;
- `cargo fmt --all -- --check`;
- `cargo test -p monad-core` including resolver unit/property/integration corpus;
- applicable repository integrity / machine-document synchronization / EOS checks required by the change gate;
- deterministic repeated-run/golden output evidence;
- explicit mapping from tests to US-018/019/020 and every Work Packet acceptance item.

Evidence generation/verification is not performed by this readiness-only refinement.

## Dependencies

### Satisfied now

- WP-MVP-0003 stable identity is complete/canonical.
- WP-MVP-0004 Markdown parser is CLOSED and canonical.
- ADR-0002/0003/0004/0005 are Accepted.
- IFC-WORKSPACE-0001, DATA-SOURCE-0001, TECH-WORKSPACE-0001, and TECH-INGEST-0001/0002/0003 are approved.
- WC-MVP-0002 is ACTIVE and explicitly includes WP-MVP-0006.
- no external service, network dependency, provider capability, secret, hosted environment, or native tool is needed by the resolver itself.

### Start-gated predecessor

- WP-MVP-0005 must formally close and its accepted implementation must be canonical on `main` before authorization/execution begins.

## Risks and disposition

### R1 — parser governed-namespace coverage is incomplete

**Observed:** current parser allowlist omits canonical families such as `IFC` and `MKE`.  
**Disposition:** bounded integration correction in #496; share one governed-identifier predicate/registry rather than adding resolver-only guessing. No ADR required.

### R2 — missing versus noncanonical classification could tempt filesystem probing

**Disposition:** classify from complete parsed index + effective include/exclude policy. Do not test target existence through the filesystem. #497/#501 prove the boundary.

### R3 — anchor semantics differ by Markdown renderer

**Disposition:** fragment is opaque provenance and target identity remains document-level. Renderer-specific slug/existence validation is out of scope. No current decision required.

### R4 — case behavior differs across host filesystems

**Disposition:** exact canonical case is authoritative; case folding is diagnostic-only. Existing discovery collision evidence remains separate. #497/#499/#501 cover it.

### R5 — duplicate governed IDs are already invalid identity state

**Disposition:** retain all duplicate targets and emit `ambiguous`; never hide existing identity diagnostics or choose a winner. Later semantic validation controls blocking severity.

### R6 — typed relation candidates could accidentally predefine graph ontology

**Disposition:** resolver `ReferenceKind`/`rule_id` describe syntactic resolution provenance only. Final graph edge types remain WP-MVP-0007 scope.

### R7 — post-WP-MVP-0005 concrete Rust type names may differ before merge

**Disposition:** semantics bind to the accepted merged configuration contract, not a provisional PR type name. At authorization, implementation begins from resulting canonical `main`; material contract drift requires a readiness correction before execution, not guessing.

### R8 — product-wide diagnostic schema is not yet implemented

**Disposition:** bounded resolver diagnostic enum only; do not promise future public code/severity schema before WP-MVP-0011.

### R9 — special files/symlinks can be hazardous if resolver touches targets

**Disposition:** resolver is in-memory/pure with respect to target filesystem. Discovery owns containment; #501 includes negative tests.

## Specification / ADR disposition

### ADRs

No new ADR is required. Existing ADR-0002 through ADR-0005 decide the relevant authority, identity, trust boundary, deterministic ingestion behavior, and Rust/module topology.

### Specifications

No new specification is required before authorization. `TECH-INGEST-0003` already decides the essential resolution semantics.

One bounded conformance clarification/correction is expected under #496 if implementation changes the Markdown parser's governed-namespace registry: the affected parser contract/version and `TECH-INGEST-0001` documentation should be updated together as required by the existing versioned-parser rule. This is not a new architectural decision.

## Out of scope

- semantic graph node/edge materialization;
- graph ontology and semantic relationship type definitions;
- semantic validation policy deciding which unresolved references are errors;
- natural-language relation inference;
- LLM/model use;
- renderer-specific Markdown anchor slug/existence validation;
- arbitrary MDX/HTML execution;
- network resolution/fetching;
- package-manager/module/import resolution;
- filesystem target probing or content execution;
- native tool execution;
- CLI presentation changes beyond any minimal compile/export wiring required by the core module;
- EOS lifecycle mutation or authorization as part of this readiness artifact.

## Readiness disposition

Against `engineering/definition-of-ready.md`, the packet now has:

- stable ID/title/owner/increment/cycle;
- observable bounded outcome and exclusions;
- explicit governing requirements/ADRs/specifications;
- exact predecessor/start gate;
- source/target/reference semantics;
- success, missing, ambiguous, noncanonical, external, invalid, security, case, cycle, and duplicate behavior;
- expected `monad-core` data/API boundary;
- six bounded implementation/test Tasks (#496–#501);
- deterministic fixture/property/security/integration strategy;
- explicit evidence expectations;
- assessed security/data/operational impacts;
- no hidden external service, credential, provider, or environment dependency;
- no unresolved strategic or product decision requiring human input.

**Readiness conclusion:** `READY_TO_AUTHORIZE` immediately after WP-MVP-0005 is formally closed/canonical and the WC-MVP-0002 one-at-a-time WIP gate permits the next packet. This conclusion does **not** authorize, start, or execute WP-MVP-0006.