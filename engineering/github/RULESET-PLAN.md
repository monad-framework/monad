# Main Branch Ruleset Plan

**Status:** Staged; apply only after the Foundation Stabilization PR passes and is merged.  
**Target:** default branch `main`

## Objectives

- prevent accidental deletion of `main`;
- prevent non-fast-forward/force-push history rewriting;
- require changes to enter through pull requests;
- require conversation/review-thread resolution before merge;
- preserve solo-founder usability while still using PR/CI evidence.

## Initial rule posture

The staged payload in `engineering/github/rulesets/main.json` requires pull requests but sets required approving reviews to zero. This is intentional for the current solo-founder phase: the PR is still the acceptance container, CI still runs, and human acceptance remains explicit without inventing a second approver.

The initial payload does **not** hard-code required status-check context names. Required checks should be added only after the stabilization PR confirms the stable check names produced by GitHub Actions. This avoids locking `main` behind a misspelled or renamed context.

## Post-stabilization hardening

After the stabilization PR:

1. confirm the stable check contexts for Repository Integrity and EOS Integrity;
2. add them to required status checks;
3. retain deletion/non-fast-forward protection;
4. keep bypass narrowly scoped to true repository recovery/admin needs;
5. revisit required approvals when another maintainer can genuinely review changes.

## Change control

Ruleset relaxation is a governance change. Do not temporarily disable protections simply to merge a failing change; fix the change, update the governing policy with rationale, or use an explicit emergency/recovery procedure.
