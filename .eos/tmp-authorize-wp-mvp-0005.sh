#!/usr/bin/env bash
set -Eeuo pipefail

EXPECTED_MAIN_HEAD="894dcd3de8640d0e4413a97ea18b7480f6209d75"
export EOS_ACTOR="Thomas Carter"

git fetch origin main
test "$(git rev-parse origin/main)" = "$EXPECTED_MAIN_HEAD"
git merge-base --is-ancestor "$EXPECTED_MAIN_HEAD" HEAD

# Authorization begins from the canonical READY boundary.
grep -q $'^WP-MVP-0001\t.*\tCLOSED\t' .eos/work-packets.tsv
grep -q $'^WP-MVP-0002\t.*\tCLOSED\t' .eos/work-packets.tsv
grep -q $'^WP-MVP-0003\t.*\tCLOSED\t' .eos/work-packets.tsv
grep -q $'^WP-MVP-0004\t.*\tCLOSED\t' .eos/work-packets.tsv
grep -q $'^WP-MVP-0005\t.*\tREADY\t' .eos/work-packets.tsv
! grep -q $'^WP-MVP-0005\t.*\tAUTHORIZED\t' .eos/work-packets.tsv
grep -q $'^WC-MVP-0002\t.*\tACTIVE\t' .eos/work-cycles.tsv
grep -q $'^PI-MVP-001\t.*\tACTIVE\t' .eos/program-increments.tsv
! grep -q $'\tWP-MVP-0005\t' .eos/executions.tsv

# Remove bootstrap-only files before producing the governed final tree.
rm .github/workflows/temporary-wp-mvp-0005-authorize.yml
rm .eos/wp-mvp-0005-authorize-trigger
rm .eos/tmp-authorize-wp-mvp-0005.sh

# Explain and execute only the authorization gate.
./scripts/eos gate explain WP_AUTHORIZE WP-MVP-0005
./scripts/eos authorize WP-MVP-0005

grep -q $'^WP-MVP-0005\t.*\tAUTHORIZED\t' .eos/work-packets.tsv
! grep -q $'\tWP-MVP-0005\t' .eos/executions.tsv
grep -q '^\*\*Status:\*\* AUTHORIZED' engineering/work-packets/WP-MVP-0005.md

python3 - <<'PY'
from pathlib import Path

status_path = Path('engineering/project-status.md')
text = status_path.read_text(encoding='utf-8')
replacements = {
    '**Current packet:** WP-MVP-0005 — READY; authorization not yet granted  ': '**Current packet:** WP-MVP-0005 — AUTHORIZED; start not yet executed  ',
    '**Current product implementation:** WP-MVP-0001–0004 closed; WP-MVP-0005 is adopted into EOS and READY, with no implementation authorization yet': '**Current product implementation:** WP-MVP-0001–0004 closed; WP-MVP-0005 is AUTHORIZED but not started or under implementation',
    'WP-MVP-0005 is the next critical-path packet. Its historical prerequisite blockers are resolved and it has passed governed adoption/Ready; it remains unauthorized and unstarted until the separate `WP_AUTHORIZE` and EOSE start gates pass.': 'WP-MVP-0005 is the next critical-path packet. Its historical prerequisite blockers are resolved and it has passed governed adoption/Ready plus the separate `WP_AUTHORIZE` gate; it remains unstarted until the separate EOSE start gate passes. No product implementation is active yet.',
    '| WC-MVP-0002 | ACTIVE | canonical cycle contract | evaluate the separate WP-MVP-0005 authorization gate; do not start implicitly |': '| WC-MVP-0002 | ACTIVE | canonical cycle contract | execute the separate WP-MVP-0005 EOSE start gate; do not begin implementation implicitly |',
    '| WP-MVP-0005 | READY / NOT AUTHORIZED | canonical packet + EOS adoption/Ready evidence + resolved prerequisites | evaluate separate `WP_AUTHORIZE`; do not start implicitly |': '| WP-MVP-0005 | AUTHORIZED / NOT STARTED | canonical packet + EOS adoption/Ready/authorization evidence | execute separate EOSE start transition; do not implement before start |',
    '1. Evaluate the separate `WP_AUTHORIZE` gate for WP-MVP-0005; authorize only through its own governed transaction if the gate passes.\n2. Start and execute WP-MVP-0005 only after authorization and the separate EOSE start transition.\n3. Refine/execute WP-MVP-0006 after its parser dependencies are accepted.\n4. Close WC-MVP-0002 only when its Sprint Goal and WP-MVP-0004–0006 exit criteria have evidence.\n5. Continue WC-MVP-0003/0004 to M-001 Semantic Kernel Alpha.\n6. Preserve MVP Release 1 scope through M-003/PG-001 acceptance.\n7. Begin PI-EXP-001 only after the MVP release boundary or explicit governed replanning.': '1. Execute the separate EOSE start transition for WP-MVP-0005; do not begin product implementation before that gate passes.\n2. Execute and verify WP-MVP-0005 against its bounded acceptance contract after start.\n3. Refine/execute WP-MVP-0006 after its parser dependencies are accepted.\n4. Close WC-MVP-0002 only when its Sprint Goal and WP-MVP-0004–0006 exit criteria have evidence.\n5. Continue WC-MVP-0003/0004 to M-001 Semantic Kernel Alpha.\n6. Preserve MVP Release 1 scope through M-003/PG-001 acceptance.\n7. Begin PI-EXP-001 only after the MVP release boundary or explicit governed replanning.',
    '      → WP-MVP-0005 — READY / NOT AUTHORIZED': '      → WP-MVP-0005 — AUTHORIZED / NOT STARTED',
}
for old, new in replacements.items():
    if old not in text:
        raise SystemExit(f'missing expected project-status text: {old!r}')
    text = text.replace(old, new, 1)
status_path.write_text(text, encoding='utf-8')

wp_path = Path('engineering/work-packets/WP-MVP-0005.md')
wp = wp_path.read_text(encoding='utf-8')
old_dependency = 'These historical prerequisite blockers are satisfied. This packet does not reimplement configuration precedence and is not Ready, authorized, or started merely because its prerequisites are complete; those lifecycle transitions require their separate governed EOS gates.'
new_dependency = 'These historical prerequisite blockers are satisfied. This packet does not reimplement configuration precedence. Prerequisite completion alone did not make the packet Ready, authorized, or started; those lifecycle transitions require separate governed EOS gates.'
if old_dependency not in wp:
    raise SystemExit('missing expected WP-MVP-0005 dependency lifecycle sentence')
wp = wp.replace(old_dependency, new_dependency, 1)
old_disposition = '''## Readiness disposition

The prior dependency block is cleared by canonical closure/acceptance evidence for WP-MVP-0001 and WP-MVP-0003 plus the Accepted ADR-0005. This packet has now been adopted into canonical EOS lifecycle control and has passed the `WP_READY` gate (`DRAFT → READY`). The next permitted lifecycle action is the separate `WP_AUTHORIZE` gate. Implementation authorization, execution preparation, start, and product mutation remain prohibited until their corresponding governed EOS gates pass and are recorded.
'''
new_disposition = '''## Authorization disposition

The prior dependency block is cleared by canonical closure/acceptance evidence for WP-MVP-0001 and WP-MVP-0003 plus the Accepted ADR-0005. This packet was adopted into canonical EOS lifecycle control, passed `WP_READY` (`DRAFT → READY`), and has now passed the separate `WP_AUTHORIZE` gate (`READY → AUTHORIZED`). The next permitted lifecycle action is the separate EOSE start transition. Execution preparation, start, product mutation, and implementation remain prohibited until that governed start transition passes and is recorded.
'''
if old_disposition not in wp:
    raise SystemExit('missing expected WP-MVP-0005 readiness disposition')
wp_path.write_text(wp.replace(old_disposition, new_disposition, 1), encoding='utf-8')
PY

# Authorization/status changes alter the semantic source fingerprint. Refresh
# current evidence for already-closed packets before strict EOSV.
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

# Reassert the authorization-only boundary after all generated refreshes.
grep -q $'^WP-MVP-0005\t.*\tAUTHORIZED\t' .eos/work-packets.tsv
! grep -q $'\tWP-MVP-0005\t' .eos/executions.tsv
grep -q $'^WC-MVP-0002\t.*\tACTIVE\t' .eos/work-cycles.tsv
grep -q $'^PI-MVP-001\t.*\tACTIVE\t' .eos/program-increments.tsv
grep -q '^\*\*Current packet:\*\* WP-MVP-0005 — AUTHORIZED; start not yet executed' engineering/project-status.md

# No product/specification/architecture mutation is permitted here.
mapfile -t changed < <({ git diff --name-only "$EXPECTED_MAIN_HEAD"; git ls-files --others --exclude-standard; } | sort -u)
test "${#changed[@]}" -gt 0
for f in "${changed[@]}"; do
  case "$f" in
    .eos/*|engineering/project-status.md|engineering/work-packets/WP-MVP-0005.md|engineering/evidence/*|machine/*) ;;
    *) echo "Out-of-scope EOSP authorization path: $f" >&2; exit 1 ;;
  esac
done

git config user.name "ChatGPT"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git add -A
git commit -m "chore(eosp): authorize WP-MVP-0005"

# Prove the committed fixed point.
./scripts/eos verify --strict
./scripts/eos state status
python3 scripts/sync-machine-docs.py --check
test -z "$(git status --porcelain)"
git push origin "HEAD:${GITHUB_REF_NAME}"
