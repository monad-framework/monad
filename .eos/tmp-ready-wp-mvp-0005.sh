#!/usr/bin/env bash
set -Eeuo pipefail

EXPECTED_MAIN_HEAD="9b21d13843d33e7c727f9a96959ac80a5e3a77b8"
export EOS_ACTOR="Thomas Carter"

git fetch origin main
test "$(git rev-parse origin/main)" = "$EXPECTED_MAIN_HEAD"
git merge-base --is-ancestor "$EXPECTED_MAIN_HEAD" HEAD

# The readiness transaction must begin from the reconciled boundary.
grep -q $'^WP-MVP-0001\t.*\tCLOSED\t' .eos/work-packets.tsv
grep -q $'^WP-MVP-0002\t.*\tCLOSED\t' .eos/work-packets.tsv
grep -q $'^WP-MVP-0003\t.*\tCLOSED\t' .eos/work-packets.tsv
grep -q $'^WP-MVP-0004\t.*\tCLOSED\t' .eos/work-packets.tsv
! grep -q $'^WP-MVP-0005\t' .eos/work-packets.tsv
grep -q $'^WC-MVP-0002\t.*\tACTIVE\t' .eos/work-cycles.tsv
grep -q $'^PI-MVP-001\t.*\tACTIVE\t' .eos/program-increments.tsv
grep -q '^\*\*Status:\*\* Refined — prerequisites satisfied; Ready gate not yet executed' engineering/work-packets/WP-MVP-0005.md

# Remove bootstrap-only files before producing the governed final tree.
rm .github/workflows/temporary-wp-mvp-0005-ready.yml
rm .eos/wp-mvp-0005-ready-trigger
rm .eos/tmp-ready-wp-mvp-0005.sh

# Dry-run first; then adopt at DRAFT and execute only the Ready gate.
./scripts/eos adopt .eos/adoptions/wp-mvp-0005.json --by "Thomas Carter"
./scripts/eos adopt .eos/adoptions/wp-mvp-0005.json --apply --by "Thomas Carter"
./scripts/eos gate explain WP_READY WP-MVP-0005
./scripts/eos ready WP-MVP-0005

# Stop at READY. Authorization/start/execution are explicitly out of scope.
grep -q $'^WP-MVP-0005\t.*\tREADY\t' .eos/work-packets.tsv
! grep -q $'^WP-MVP-0005\t.*\tAUTHORIZED\t' .eos/work-packets.tsv
grep -q '^\*\*Status:\*\* READY' engineering/work-packets/WP-MVP-0005.md

python3 - <<'PY'
from pathlib import Path

status_path = Path('engineering/project-status.md')
text = status_path.read_text(encoding='utf-8')
replacements = {
    '**Current packet:** WP-MVP-0005 — REFINED; Ready gate not yet executed  ': '**Current packet:** WP-MVP-0005 — READY; authorization not yet granted  ',
    '**Current product implementation:** WP-MVP-0001–0004 closed; WP-MVP-0005 is the next critical-path packet and is not yet authorized for execution': '**Current product implementation:** WP-MVP-0001–0004 closed; WP-MVP-0005 is adopted into EOS and READY, with no implementation authorization yet',
    'WP-MVP-0005 is the next critical-path packet. Its historical prerequisite blockers are resolved, but it remains only refined until its Ready/adoption gate is executed and recorded; readiness does not imply authorization or execution.': 'WP-MVP-0005 is the next critical-path packet. Its historical prerequisite blockers are resolved and it has passed governed adoption/Ready; it remains unauthorized and unstarted until the separate `WP_AUTHORIZE` and EOSE start gates pass.',
    '| WC-MVP-0002 | ACTIVE | canonical cycle contract | ready/adopt WP-MVP-0005, then authorize only if its gates pass |': '| WC-MVP-0002 | ACTIVE | canonical cycle contract | evaluate the separate WP-MVP-0005 authorization gate; do not start implicitly |',
    '| WP-MVP-0005 | REFINED / NOT READY | canonical packet + resolved WP-MVP-0001/WP-MVP-0003/ADR-0005 prerequisites | execute governed Ready/adoption gate; do not authorize implicitly |': '| WP-MVP-0005 | READY / NOT AUTHORIZED | canonical packet + EOS adoption/Ready evidence + resolved prerequisites | evaluate separate `WP_AUTHORIZE`; do not start implicitly |',
    '1. Reconcile repository/GitHub status projections to the canonical WP-MVP-0004 closure state.\n2. Complete WP-MVP-0005 readiness/adoption against the now-resolved WP-MVP-0001, WP-MVP-0003, and ADR-0005 prerequisites.\n3. Authorize/start/execute WP-MVP-0005 only after its Ready and EOS authorization gates pass.\n4. Refine/execute WP-MVP-0006 after its parser dependencies are accepted.\n5. Close WC-MVP-0002 only when its Sprint Goal and WP-MVP-0004–0006 exit criteria have evidence.\n6. Continue WC-MVP-0003/0004 to M-001 Semantic Kernel Alpha.\n7. Preserve MVP Release 1 scope through M-003/PG-001 acceptance.\n8. Begin PI-EXP-001 only after the MVP release boundary or explicit governed replanning.': '1. Evaluate the separate `WP_AUTHORIZE` gate for WP-MVP-0005; authorize only through its own governed transaction if the gate passes.\n2. Start and execute WP-MVP-0005 only after authorization and the separate EOSE start transition.\n3. Refine/execute WP-MVP-0006 after its parser dependencies are accepted.\n4. Close WC-MVP-0002 only when its Sprint Goal and WP-MVP-0004–0006 exit criteria have evidence.\n5. Continue WC-MVP-0003/0004 to M-001 Semantic Kernel Alpha.\n6. Preserve MVP Release 1 scope through M-003/PG-001 acceptance.\n7. Begin PI-EXP-001 only after the MVP release boundary or explicit governed replanning.',
    '      → WP-MVP-0005 — REFINED / NOT READY': '      → WP-MVP-0005 — READY / NOT AUTHORIZED',
}
for old, new in replacements.items():
    if old not in text:
        raise SystemExit(f'missing expected project-status text: {old!r}')
    text = text.replace(old, new, 1)
status_path.write_text(text, encoding='utf-8')

wp_path = Path('engineering/work-packets/WP-MVP-0005.md')
wp = wp_path.read_text(encoding='utf-8')
old = '''## Readiness disposition

The prior dependency block is cleared by canonical closure/acceptance evidence for WP-MVP-0001 and WP-MVP-0003 plus the Accepted ADR-0005. The next permitted lifecycle action is governed readiness/adoption. Implementation authorization, execution preparation, and product mutation remain prohibited until the corresponding EOS gates pass and are recorded.
'''
new = '''## Readiness disposition

The prior dependency block is cleared by canonical closure/acceptance evidence for WP-MVP-0001 and WP-MVP-0003 plus the Accepted ADR-0005. This packet has now been adopted into canonical EOS lifecycle control and has passed the `WP_READY` gate (`DRAFT → READY`). The next permitted lifecycle action is the separate `WP_AUTHORIZE` gate. Implementation authorization, execution preparation, start, and product mutation remain prohibited until their corresponding governed EOS gates pass and are recorded.
'''
if old not in wp:
    raise SystemExit('missing expected WP-MVP-0005 readiness disposition')
wp_path.write_text(wp.replace(old, new, 1), encoding='utf-8')
PY

# Readiness/adoption changes the semantic source fingerprint. Refresh current
# evidence for already-closed packets before strict EOSV.
./scripts/eos validate WP-MVP-0001 --profile wp
./scripts/eos validate WP-MVP-0002 --profile wp --execution EXEC-0004
./scripts/eos validate WP-MVP-0003 --profile wp --execution EXEC-0005
./scripts/eos validate WP-MVP-0004 --profile wp --execution EXEC-0009

python3 tools/eos/trace_integrity.py --write
python3 scripts/sync-machine-docs.py --write
./scripts/eos verify --strict
./scripts/eos state status
python3 tools/eos/trace_integrity.py
python3 scripts/sync-machine-docs.py --check

# Reassert lifecycle boundary after all generated refreshes.
grep -q $'^WP-MVP-0005\t.*\tREADY\t' .eos/work-packets.tsv
! grep -q $'^WP-MVP-0005\t.*\tAUTHORIZED\t' .eos/work-packets.tsv
grep -q $'^WC-MVP-0002\t.*\tACTIVE\t' .eos/work-cycles.tsv
grep -q $'^PI-MVP-001\t.*\tACTIVE\t' .eos/program-increments.tsv
grep -q '^\*\*Current packet:\*\* WP-MVP-0005 — READY; authorization not yet granted' engineering/project-status.md

# No product/specification/architecture mutation is permitted here.
mapfile -t changed < <({ git diff --name-only "$EXPECTED_MAIN_HEAD"; git ls-files --others --exclude-standard; } | sort -u)
test "${#changed[@]}" -gt 0
for f in "${changed[@]}"; do
  case "$f" in
    .eos/*|engineering/project-status.md|engineering/work-packets/WP-MVP-0005.md|engineering/evidence/*|machine/*) ;;
    *) echo "Out-of-scope EOSP Ready path: $f" >&2; exit 1 ;;
  esac
done

git config user.name "ChatGPT"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git add -A
git commit -m "chore(eosp): ready WP-MVP-0005"

# Prove the committed fixed point, not only the pre-commit workspace.
./scripts/eos verify --strict
./scripts/eos state status
python3 scripts/sync-machine-docs.py --check
test -z "$(git status --porcelain)"
git push origin "HEAD:${GITHUB_REF_NAME}"
