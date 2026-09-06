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
  local mode="${1:-core}"
  local p fields_json
  p="$(project_number)"
  if [[ -z "$p" ]]; then
    echo "Creating GitHub Project '$PROJECT_TITLE'..."
    gh project create --owner "$ORG" --title "$PROJECT_TITLE" >/dev/null
    p="$(project_number)"
  fi
  [[ -n "$p" ]] || { echo "Could not resolve Project number." >&2; exit 3; }

  echo "Using GitHub Project #$p: $PROJECT_TITLE"
  gh project link "$p" --owner "$ORG" --repo "$ORG/$REPO" >/dev/null 2>&1 || true

  fields_json="$(gh project field-list "$p" --owner "$ORG" --format json --limit 100)"

  resolve_field_name() {
    local requested="$1"
    python3 -c '
import json,re,sys
requested=sys.argv[1]
def key(value):
    return re.sub(r"[^a-z0-9]+", "", (value or "").lower())
d=json.load(sys.stdin)
wanted=key(requested)
for field in d.get("fields", []):
    if key(field.get("name")) == wanted:
        print(field.get("name") or "")
        break
' "$requested" <<<"$fields_json"
  }

  ensure_field() {
    local name="$1" type="$2" options="${3:-}" existing
    existing="$(resolve_field_name "$name")"
    [[ -n "$existing" ]] && return 0
    echo "Creating missing Project field: $name"
    if [[ "$type" == "SINGLE_SELECT" ]]; then
      gh project field-create "$p" --owner "$ORG" --name "$name" --data-type "$type" --single-select-options "$options" >/dev/null
    else
      gh project field-create "$p" --owner "$ORG" --name "$name" --data-type "$type" >/dev/null
    fi
    fields_json="$(gh project field-list "$p" --owner "$ORG" --format json --limit 100)"
  }

  echo "Checking Project fields..."
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
  echo "Project fields OK."

  sync_project_items "$p"
  python3 "$ROOT/scripts/sync-github-project-metadata.py" "$ORG" "$REPO" "$p" "$mode"

  echo "Project #$p synchronized ($mode projection)."
  echo "Create/verify views from engineering/github/PROJECT-V2-CONFIGURATION.md."
}

sync_project_items() {
  local p="$1"
  local issue_tmp existing_tmp total i added present url
  issue_tmp="$(mktemp)"
  existing_tmp="$(mktemp)"

  gh issue list -R "$ORG/$REPO" --state all --limit 1000 --json url >"$issue_tmp"
  total="$(python3 -c 'import json,sys; print(len(json.load(open(sys.argv[1]))))' "$issue_tmp")"

  echo "Checking $total repository issues against Project #$p..."
  if ! gh project item-list "$p" --owner "$ORG" --limit 1000 --format json \
      --jq '.items[] | .content.url // empty' >"$existing_tmp" 2>/dev/null; then
    : >"$existing_tmp"
    echo "NOTE: could not pre-read Project item URLs; falling back to idempotent item-add calls." >&2
  fi

  i=0
  added=0
  present=0
  while IFS= read -r url; do
    [[ -n "$url" ]] || continue
    i=$((i + 1))
    if grep -Fqx -- "$url" "$existing_tmp"; then
      present=$((present + 1))
    else
      if gh project item-add "$p" --owner "$ORG" --url "$url" >/dev/null 2>&1; then
        added=$((added + 1))
        printf '%s\n' "$url" >>"$existing_tmp"
      else
        echo "WARN: could not add Project item $url" >&2
      fi
    fi
    if (( i % 20 == 0 || i == total )); then
      echo "  Project items: $i/$total checked; $added added; $present already present"
    fi
  done < <(python3 -c 'import json,sys; [print(x["url"]) for x in json.load(open(sys.argv[1]))]' "$issue_tmp")

  rm -f "$issue_tmp" "$existing_tmp"
}

sync_wiki() {
  local tmp rc
  tmp="$(mktemp -d)"
  if ! git clone --quiet "https://github.com/$ORG/$REPO.wiki.git" "$tmp/wiki"; then
    rm -rf "$tmp"
    echo "Wiki repository is not initialized. Open the GitHub Wiki once, create its first page, then rerun this command." >&2
    return 4
  fi
  cp "$ROOT"/engineering/github/wiki/*.md "$tmp/wiki/"
  rc=0
  (
    cd "$tmp/wiki"
    git add .
    if git diff --cached --quiet; then
      echo "Wiki already synchronized."
    else
      git commit -m "docs: synchronize Monad canonical wiki projection"
      git push origin HEAD
    fi
  ) || rc=$?
  rm -rf "$tmp"
  return "$rc"
}

apply_ruleset() {
  echo "Applying staged main ruleset. Run this only after stabilization PR checks are confirmed." >&2
  gh api --method POST "repos/$ORG/$REPO/rulesets" --input "$ROOT/engineering/github/rulesets/main.json"
}

case "${1:-check}" in
  check) check ;;
  project) ensure_project core ;;
  project-full) ensure_project full ;;
  wiki) sync_wiki ;;
  ruleset) apply_ruleset ;;
  all-safe) check; ensure_project core; sync_wiki ;;
  *) echo "Usage: $0 {check|project|project-full|wiki|ruleset|all-safe}" >&2; exit 2 ;;
esac
