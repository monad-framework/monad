# .eos

Internal Engineering Operating System state.

- `workflow.tsv` — ordered bootstrap workflow
- `artifacts.tsv` — governed artifact registry
- `artifact-changelog.tsv` — semantic artifact version changes
- `history/` — retained prior governed artifact bodies
- `checkpoints/` — checkpoint metadata
- `prompts/` — generated prompt material

This directory is intentionally committed to Git except for ephemeral files.

## Permanent Lifecycle State

- `layers.tsv` — EOSB/EOSP/EOSE/EOSV/EOSR/EOSC/EOSL/EOSM;
- `program-increments.tsv` — PI state;
- `work-cycles.tsv` — WC state;
- `work-packets.tsv` — WP state;
- `change-requests.tsv` — EOSC state;
- `maintenance.tsv` — EOSM state;
- `releases.tsv` — EOSL state;
- `decisions.tsv` — gate/closure decision log;
- `trace-edges.tsv` — generated traceability graph;
- `contracts/` — Codex and ChatGPT review contracts;
- `evidence/` — verification/review evidence;
- `sync/` — GitHub sync records.
