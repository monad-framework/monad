#!/usr/bin/env bash
set -euo pipefail

ORG="${MONAD_GITHUB_ORG:-monad-framework}"
REPO="${MONAD_GITHUB_REPO:-monad}"
PROJECT_TITLE="${MONAD_GITHUB_PROJECT:-Monad Engineering Program}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

need() { command -v "$1" >/dev/null 2>&1 || { echo "Required command missing: $1" >&2; exit 2; }; }
need gh
need git
need python3

project_number() {
  gh project list --owner "$ORG" --format json --limit 100 \
    | python3 -c 'import json,sys; title=sys.argv[1]; rows=json.load(sys.stdin).get("projects",[]); matches=[r for r in rows if r.get("title")==title]; print(matches[0]["number"] if matches else "")' "$PROJECT_TITLE"
}

check() {
  echo "Repository: $ORG/$REPO"
  echo "Project:    $PROJECT_TITLE"
  gh auth status
  gh repo view "$ORG/$REPO" --json nameWithOwner,defaultBranchRef,hasIssuesEnabled,hasWikiEnabled
  local p
  p="$(project_number)"
  if [[ -n "$p" ]]; then echo "Existing Project #$p found."; else echo "Project not found; project command will create it."; fi
  echo "Current repo issue count: $(gh issue list -R "$ORG/$REPO" --state all --limit 1000 --json number | python3 -c 'import json,sys; print(len(json.load(sys.stdin)))')"
}

ensure_project() {
  local p
  p="$(project_number)"
  if [[ -z "$p" ]]; then
    gh project create --owner "$ORG" --title "$PROJECT_TITLE"
    p="$(project_number)"
  fi
  [[ -n "$p" ]] || { echo "Could not resolve Project number." >&2; exit 3; }
  gh project link "$p" --owner "$ORG" --repo "$ORG/$REPO" >/dev/null 2>&1 || true

  local fields_json
  fields_json="$(gh project field-list "$p" --owner "$ORG" --format json --limit 100)"
  ensure_field() {
    local name="$1" type="$2" options="${3:-}"
    if python3 -c 'import json,sys; n=sys.argv[1]; d=json.load(sys.stdin); raise SystemExit(0 if any(f.get("name")==n for f in d.get("fields",[])) else 1)' "$name" <<<"$fields_json"; then
      return
    fi
    if [[ "$type" == "SINGLE_SELECT" ]]; then
      gh project field-create "$p" --owner "$ORG" --name "$name" --data-type "$type" --single-select-options "$options"
    else
      gh project field-create "$p" --owner "$ORG" --name "$name" --data-type "$type"
    fi
    fields_json="$(gh project field-list "$p" --owner "$ORG" --format json --limit 100)"
  }

  ensure_field "Item Type" SINGLE_SELECT "Initiative,Epic,Feature,Story,Enabler,Work Packet,Bug,Defect,Change Request"
  ensure_field "Product Goal" TEXT
  ensure_field "Initiative" TEXT
  ensure_field "Epic" TEXT
  ensure_field "Priority" SINGLE_SELECT "P0,P1,P2,P3"
  ensure_field "Criticality" SINGLE_SELECT "C0,C1,C2,C3,C4,C5"
  ensure_field "Product Area" TEXT
  ensure_field "Domain" TEXT
  ensure_field "Increment" TEXT
  ensure_field "Sprint" TEXT
  ensure_field "Lifecycle" SINGLE_SELECT "Backlog,Refining,Ready,Authorized,Running,Review,Verified,Closed,Blocked"
  ensure_field "Story Points" NUMBER
  ensure_field "Risk" SINGLE_SELECT "Critical,High,Medium,Low"
  ensure_field "Executor" SINGLE_SELECT "Human,ChatGPT,Codex,Mixed"
  ensure_field "Work Packet" TEXT
  ensure_field "Specification" TEXT
  ensure_field "ADR" TEXT
  ensure_field "Target Release" TEXT
  ensure_field "Start Date" DATE
  ensure_field "Target Date" DATE

  gh issue list -R "$ORG/$REPO" --state all --limit 1000 --json url \
    | python3 -c 'import json,sys; [print(x["url"]) for x in json.load(sys.stdin)]' \
    | while IFS= read -r url; do
        [[ -n "$url" ]] && gh project item-add "$p" --owner "$ORG" --url "$url" >/dev/null || true
      done

  sync_project_metadata "$p"

  echo "Project #$p synchronized. Create/verify views from engineering/github/PROJECT-V2-CONFIGURATION.md."
}

sync_project_metadata() {
  local p="$1"
  local issue_tmp projection
  issue_tmp="$(mktemp)"
  trap 'rm -f "$issue_tmp"' RETURN

  gh issue list -R "$ORG/$REPO" --state all --limit 1000 --json title,body,url,state >"$issue_tmp"

  projection="$(python3 - "$issue_tmp" <<'PY'
import json,re,sys
with open(sys.argv[1], encoding='utf-8') as f:
    rows=json.load(f)

def m(pattern, text):
    x=re.search(pattern, text or '', re.I|re.M)
    return x.group(1).strip() if x else ''

def epic_to_init(epic):
    x=m(r'EPIC-(\d+)', epic)
    if not x:
        return ''
    n=int(x)
    if n == 1: return 'INIT-001'
    if 2 <= n <= 5: return 'INIT-002'
    if 6 <= n <= 7: return 'INIT-003'
    if 8 <= n <= 9: return 'INIT-004'
    if 10 <= n <= 12: return 'INIT-005'
    if 13 <= n <= 14: return 'INIT-006'
    return ''

def kind(title):
    x=m(r'^\[([^\]]+)\]', title)
    aliases={'Defect':'Defect','Bug':'Bug','Initiative':'Initiative','Epic':'Epic','Feature':'Feature','Story':'Story','Enabler':'Enabler','Change Request':'Change Request'}
    return aliases.get(x, '')

def lifecycle(row):
    body=row.get('body') or ''
    state=(row.get('state') or '').upper()
    upper=body.upper()
    if state == 'CLOSED': return 'Closed'
    if 'READY — NOT AUTHORIZED' in upper or 'READY - NOT AUTHORIZED' in upper: return 'Ready'
    if 'REMAINS **BACKLOG**' in upper: return 'Backlog'
    if '**BLOCKED' in upper: return 'Blocked'
    if '**RUNNING' in upper: return 'Running'
    if '**AUTHORIZED' in upper and 'NOT AUTHORIZED' not in upper: return 'Authorized'
    if '**VERIFIED' in upper: return 'Verified'
    if '**REVIEW' in upper: return 'Review'
    return ''

for row in rows:
    title=row.get('title') or ''
    body=row.get('body') or ''
    item_type=kind(title)
    init=m(r'(INIT-\d{3})', title) if item_type == 'Initiative' else ''
    epic=m(r'(EPIC-\d{3})', title) if item_type == 'Epic' else m(r'Parent Epic:\s*`(EPIC-\d{3})`', body)
    if not init:
        init=epic_to_init(epic)
    pg=m(r'Product Goal:\s*`([^`]+)`', body)
    if not pg and (init or epic):
        pg='PG-001'
    wp=m(r'Work Packet:\s*`([^`]+)`', body) or m(r'\b(WP-[A-Z0-9-]+)\b', title)
    sprint=m(r'(?:Work Cycle|Forecast Sprint):\s*`([^`]+)`', body)
    values=[row.get('url') or '',item_type,pg,init,epic,sprint,wp,lifecycle(row)]
    print('\t'.join(v.replace('\t',' ').replace('\n',' ') for v in values))
PY
)"

  set_field() {
    local url="$1" field="$2" value="$3"
    [[ -z "$url" || -z "$value" ]] && return 0
    if ! gh project item-edit "$p" --owner "$ORG" --url "$url" --field "$field" --value "$value" >/dev/null 2>&1; then
      echo "WARN: could not set Project field '$field'='$value' for $url" >&2
    fi
  }

  while IFS=$'\t' read -r url item_type product_goal initiative epic sprint work_packet lifecycle; do
    [[ -n "$url" ]] || continue
    set_field "$url" "Item Type" "$item_type"
    set_field "$url" "Product Goal" "$product_goal"
    set_field "$url" "Initiative" "$initiative"
    set_field "$url" "Epic" "$epic"
    set_field "$url" "Sprint" "$sprint"
    set_field "$url" "Work Packet" "$work_packet"
    set_field "$url" "Lifecycle" "$lifecycle"
  done <<<"$projection"

  python3 -c '
import json,sys
required={"Initiative","Defect"}
d=json.load(sys.stdin)
f=next((x for x in d.get("fields",[]) if x.get("name")=="Item Type"),{})
opts={o.get("name") for o in f.get("options",[])}
missing=sorted(required-opts)
print(",".join(missing))
' <<<"$fields_json" | while IFS= read -r missing; do
    if [[ -n "$missing" ]]; then
      echo "NOTE: existing Item Type field is missing option(s): $missing. Add them once in the Project UI; the next sync will populate those items." >&2
    fi
  done
}

sync_wiki() {
  local tmp
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' RETURN
  if ! git clone --quiet "https://github.com/$ORG/$REPO.wiki.git" "$tmp/wiki"; then
    echo "Wiki repository is not initialized. Open the GitHub Wiki once, create its first page, then rerun this command." >&2
    return 4
  fi
  cp "$ROOT"/engineering/github/wiki/*.md "$tmp/wiki/"
  (
    cd "$tmp/wiki"
    git add .
    if git diff --cached --quiet; then
      echo "Wiki already synchronized."
    else
      git commit -m "docs: synchronize Monad canonical wiki projection"
      git push origin HEAD
    fi
  )
}

apply_ruleset() {
  echo "Applying staged main ruleset. Run this only after stabilization PR checks are confirmed." >&2
  gh api --method POST "repos/$ORG/$REPO/rulesets" --input "$ROOT/engineering/github/rulesets/main.json"
}

case "${1:-check}" in
  check) check ;;
  project) ensure_project ;;
  wiki) sync_wiki ;;
  ruleset) apply_ruleset ;;
  all-safe) check; ensure_project; sync_wiki ;;
  *) echo "Usage: $0 {check|project|wiki|ruleset|all-safe}" >&2; exit 2 ;;
esac
