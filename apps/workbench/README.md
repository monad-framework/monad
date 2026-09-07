# Monad Workbench

Monad Workbench is the local-first, read-only engineering cockpit for the Monad repository.

Workbench v0 consumes existing canonical Monad and EOS state, normalizes it into an in-memory read model, and presents synchronized projections optimized for human comprehension. It is deliberately non-authoritative: the Workbench does not own product truth, lifecycle truth, evidence, or governance state.

## v0 surfaces

- **Now** — current Product Goal, Initiative, Epic, Feature, Stories/Enablers, Program Increment, Work Cycle, Work Packet, governing knowledge, repository state, and next-context cues.
- **Plan** — canonical product hierarchy: `Product Goal → Initiative → Epic → Feature → Story / Enabler → Task`.
- **Execution** — governed execution hierarchy: `Program Increment → Work Cycle → Work Packet → Execution → Verification / Evidence`.
- **Knowledge** — requirements, specifications, ADRs, policies, and evidence.
- **Control** — risks, change requests, reviews, verification, releases, and related control state.
- **Focus** — object-centric projection for a selected Monad object, including source, relationships, semantic document blocks, provenance, and lifecycle context.
- **Command palette** — `Ctrl/Cmd+K` search and navigation across indexed Monad objects.

Product planning and governed execution are intentionally orthogonal. A Feature may forecast or relate to one or more Work Packets, but a Work Packet is not a child level inside the product hierarchy.

## Authority and source precedence

Workbench is a consumer of repository projections. When sources overlap, v0 follows this precedence:

1. `.eos/state/current.json` for live EOS lifecycle state.
2. Canonical product planning artifacts such as `product/PROGRAM-HIERARCHY.md`, `product/initiatives.md`, and the approved backlogs.
3. Authoritative engineering artifacts such as Work Packet Markdown for objectives, acceptance criteria, dependencies, and governing references.
4. EOS registries and trace/evidence projections such as `.eos/*.tsv`.
5. Git workspace metadata for branch and working-tree context.

If an authored narrative and canonical EOS current state disagree, Workbench treats the canonical EOS state as lifecycle authority and presents the authored content as artifact narrative rather than silently promoting it.

## Requirements

- Bun 1.3.x
- Node-compatible environment required by Next.js 16
- a checkout of the Monad repository containing `monad.toml`

Workbench discovers the repository root by walking upward from its current working directory until it finds `monad.toml`.

## Install

From `apps/workbench`:

```bash
bun install --frozen-lockfile
```

## Development

```bash
bun run dev
```

Open `http://localhost:3000`.

The application is intended to run inside a local Monad checkout. No database, authentication service, Supabase project, Payload instance, or cloud account is required for v0.

## Verification

Run the complete v0 gate:

```bash
bun run check
```

Or run each stage separately:

```bash
bun run lint
bun run test
bun run build
```

`bun run test` covers the highest-risk adapter boundaries, including product hierarchy parsing, EOS execution projection, TSV normalization, Focus document path containment, and repository-root discovery.

## Keyboard and shell behavior

- `Ctrl/Cmd+K` — open command palette.
- `Ctrl/Cmd+B` — collapse/expand Navigator.
- `Ctrl/Cmd+Shift+B` — collapse/expand Inspector.
- `Escape` — close menus, context menus, or command palette.
- Right-click — open the Workbench context menu.

Navigator and Inspector collapsed state are local UI preferences persisted in browser `localStorage`; they are not Monad engineering state.

## v0 non-goals

Workbench v0 intentionally does **not** provide:

- authoritative state mutation;
- EOS lifecycle transitions;
- governed write/edit workflows;
- AI execution control;
- production authentication or tenancy;
- cloud persistence;
- realtime collaboration;
- persistent multi-tab workspaces;
- a generalized plugin system;
- a graph database;
- a replacement code editor.

Those capabilities belong to later Workbench versions. The v0 contract is trustworthy local comprehension and navigation.

## Architecture

```text
Canonical Monad / EOS sources
            │
            ▼
     Workbench adapters
            │
            ▼
      in-memory read model
            │
            ▼
  projection/index functions
            │
            ▼
     Next.js Workbench UI
```

The intended evolution is for more of the temporary Workbench-specific ingestion layer to be replaced by stable Monad semantic-kernel/query interfaces while preserving the user-facing projection model.

## Implementation specification

See `docs/implementation/workbench-v0.md` from the repository root.
