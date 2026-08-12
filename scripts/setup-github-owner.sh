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

  ensure_field "Item Type" SINGLE_SELECT "Epic,Feature,Story,Enabler,Work Packet,Bug,Change Request"
  ensure_field "Priority" SINGLE_SELECT "P0,P1,P2,P3"
  ensure_field "Criticality" SINGLE_SELECT "C0,C1,C2,C3,C4,C5"
  ensure_field "Product Area" TEXT
  ensure_field "Increment" TEXT
  ensure_field "Sprint" TEXT
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

  echo "Project #$p synchronized. Create/verify views from engineering/github/PROJECT-V2-CONFIGURATION.md."
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
