# GitHub Wiki Plan

**Status:** Proposed  
**Authority:** Informational projection only

The Monad Wiki is an orientation and navigation layer for humans. It MUST NOT become the canonical location for architecture, specifications, requirements, decisions, Work Packets, or release evidence.

## Canonical page source

Wiki page source is staged under `engineering/github/wiki/`. The owner synchronization process copies these pages into the separate GitHub Wiki repository.

## Initial pages

- `Home.md` — product identity and navigation.
- `Engineering-Operating-System.md` — EOS layers and operating loop.
- `MVP-Roadmap.md` — current release goal and milestone sequence.
- `Artifact-Authority.md` — canonical-vs-projection authority model.
- `Working-With-ChatGPT-and-Codex.md` — human/ChatGPT/Codex/GitHub responsibility split.

## Update rule

Wiki edits should originate from the canonical staged pages or be reconciled back immediately. Meaning-changing engineering decisions MUST be made in their canonical Git artifact first, then reflected into the Wiki.

## Link strategy

Wiki pages should link readers back to repository paths for authoritative detail. Avoid copying large normative documents into the Wiki because duplicated normative text will drift.
