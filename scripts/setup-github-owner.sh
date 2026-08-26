#!/usr/bin/env bash
set -euo pipefail

ORG="${MONAD_GITHUB_ORG:-monad-framework}"
REPO="${MONAD_GITHUB_REPO:-monad}"
PROJECT_TITLE="${MONAD_GITHUB_PROJECT:-Monad Engineering Program}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

need() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Required command missing: $1" >&2
    exit 2
  }
}

need gh
need git
need python3

project_number() {
  gh project list --owner "$ORG" --format json --limit 100 \
    | python3 -c '
import json
import sys

title = sys.argv[1]
data = json.load(sys.stdin)
rows = data.get("projects", []) if isinstance(data, dict) else data
matches = [row for row in rows if row.get("title") == title]
print(matches[0]["number"] if matches else "")
' "$PROJECT_TITLE"
}

field_list_json() {
  local project_number="$1"

  gh project field-list "$project_number" \
    --owner "$ORG" \
    --format json \
    --limit 100
}

field_exists_in_json() {
  local name="$1"

  python3 -c '
import json
import sys

target = " ".join(sys.argv[1].split()).casefold()
data = json.load(sys.stdin)

if isinstance(data, dict):
    fields = data.get("fields", [])
elif isinstance(data, list):
    fields = data
else:
    fields = []

exists = any(
    " ".join((field.get("name") or "").split()).casefold() == target
    for field in fields
    if isinstance(field, dict)
)

raise SystemExit(0 if exists else 1)
' "$name"
}

is_duplicate_field_error() {
  local output="$1"

  [[ "$output" == *"Name has already been taken"* ]] \
    && [[ "$output" == *"createProjectV2Field"* ]]
}

check() {
  echo "Repository: $ORG/$REPO"
  echo "Project:    $PROJECT_TITLE"

  gh auth status
  gh repo view "$ORG/$REPO" \
    --json nameWithOwner,defaultBranchRef,hasIssuesEnabled,hasWikiEnabled

  local p
  p="$(project_number)"

  if [[ -n "$p" ]]; then
    echo "Existing Project #$p found."
  else
    echo "Project not found; project command will create it."
  fi

  echo "Current repo issue count: $(
    gh issue list -R "$ORG/$REPO" \
      --state all \
      --limit 1000 \
      --json number \
      | python3 -c 'import json,sys; print(len(json.load(sys.stdin)))'
  )"
}

ensure_project() {
  local p
  p="$(project_number)"

  if [[ -z "$p" ]]; then
    echo "Creating organization Project: $PROJECT_TITLE"
    gh project create --owner "$ORG" --title "$PROJECT_TITLE"
    p="$(project_number)"
  fi

  [[ -n "$p" ]] || {
    echo "Could not resolve Project number." >&2
    exit 3
  }

  echo "Using Project #$p: $PROJECT_TITLE"

  # Linking is idempotent from the perspective of this bootstrap. GitHub may
  # report an already-linked repository as an error, which is safe to ignore.
  gh project link "$p" \
    --owner "$ORG" \
    --repo "$ORG/$REPO" \
    >/dev/null 2>&1 || true

  ensure_field() {
    local name="$1"
    local type="$2"
    local options="${3:-}"
    local fields_json
    local create_output
    local create_rc

    # Always fetch the live field list for each field. Do not rely on a cached
    # snapshot from before previous create operations.
    fields_json="$(field_list_json "$p")"

    if field_exists_in_json "$name" <<<"$fields_json"; then
      echo "Field already exists: $name"
      return 0
    fi

    echo "Creating field: $name ($type)"

    create_rc=0
    if [[ "$type" == "SINGLE_SELECT" ]]; then
      create_output="$(
        gh project field-create "$p" \
          --owner "$ORG" \
          --name "$name" \
          --data-type "$type" \
          --single-select-options "$options" \
          2>&1
      )" || create_rc=$?
    else
      create_output="$(
        gh project field-create "$p" \
          --owner "$ORG" \
          --name "$name" \
          --data-type "$type" \
          2>&1
      )" || create_rc=$?
    fi

    if (( create_rc == 0 )); then
      [[ -z "$create_output" ]] || echo "$create_output"
      return 0
    fi

    # GitHub enforces project-field name uniqueness. A partially completed
    # bootstrap may therefore return this specific GraphQL error even when the
    # CLI field-list result did not expose the colliding configuration.
    #
    # Treat only the precise duplicate-name mutation failure as idempotent.
    # Do not swallow authentication, authorization, schema, network, or other
    # GraphQL failures.
    if is_duplicate_field_error "$create_output"; then
      echo "Field already exists according to GitHub: $name"

      # Best-effort refresh for observability. A duplicate response is already
      # authoritative enough to continue safely if the field remains absent
      # from the CLI listing.
      fields_json="$(field_list_json "$p")"
      if ! field_exists_in_json "$name" <<<"$fields_json"; then
        echo \
          "Warning: GitHub reports '$name' already exists, but gh project field-list does not expose it; continuing without creating a duplicate." \
          >&2
      fi

      return 0
    fi

    echo "$create_output" >&2
    return "$create_rc"
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

  echo "Synchronizing repository issues into Project #$p..."

  gh issue list -R "$ORG/$REPO" \
    --state all \
    --limit 1000 \
    --json url \
    | python3 -c '
import json
import sys

for item in json.load(sys.stdin):
    url = item.get("url")
    if url:
        print(url)
' \
    | while IFS= read -r url; do
        if [[ -n "$url" ]]; then
          # item-add can report that an item is already present. Existing
          # membership is safe for this synchronization operation.
          gh project item-add "$p" \
            --owner "$ORG" \
            --url "$url" \
            >/dev/null 2>&1 || true
        fi
      done

  echo "Project #$p synchronized."
  echo "Create/verify views from engineering/github/PROJECT-V2-CONFIGURATION.md."
}

sync_wiki() {
  local tmp
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' RETURN

  if ! git clone --quiet "https://github.com/$ORG/$REPO.wiki.git" "$tmp/wiki"; then
    echo \
      "Wiki repository is not initialized. Open the GitHub Wiki once, create its first page, then rerun this command." \
      >&2
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
  echo \
    "Applying staged main ruleset. Run this only after stabilization PR checks are confirmed." \
    >&2

  gh api \
    --method POST \
    "repos/$ORG/$REPO/rulesets" \
    --input "$ROOT/engineering/github/rulesets/main.json"
}

case "${1:-check}" in
  check)
    check
    ;;
  project)
    ensure_project
    ;;
  wiki)
    sync_wiki
    ;;
  ruleset)
    apply_ruleset
    ;;
  all-safe)
    check
    ensure_project
    sync_wiki
    ;;
  *)
    echo "Usage: $0 {check|project|wiki|ruleset|all-safe}" >&2
    exit 2
    ;;
esac
