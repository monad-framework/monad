#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

WORKFLOW=".eos/workflow.tsv"
REGISTRY=".eos/artifacts.tsv"
CHANGELOG=".eos/artifact-changelog.tsv"

die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
warn() { printf 'WARNING: %s\n' "$*" >&2; }
now_iso() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }

usage() {
  cat <<'EOF'
Engineering Operating System

Usage:
  ./scripts/eos status
  ./scripts/eos next
  ./scripts/eos prompt <EOSB-NNN>
  ./scripts/eos complete <EOSB-NNN>
  ./scripts/eos reopen <EOSB-NNN>
  ./scripts/eos version <artifact.md> <patch|minor|major> <message>
  ./scripts/eos history <artifact.md>
  ./scripts/eos rollback <artifact.md> <version> <message>
  ./scripts/eos checkpoint <message>
  ./scripts/eos verify
  ./scripts/eos responsibilities
EOF
}

frontmatter_value() {
  local file="$1"
  local key="$2"
  awk -F': ' -v k="$key" '
    NR <= 40 && $1 == k {
      v=$2
      gsub(/^"/, "", v)
      gsub(/"$/, "", v)
      print v
      exit
    }
  ' "$file"
}

replace_frontmatter_value() {
  local file="$1"
  local key="$2"
  local value="$3"
  local tmp
  tmp="$(mktemp)"
  awk -v k="$key" -v v="$value" '
    BEGIN { changed=0 }
    NR <= 40 && index($0, k ":") == 1 && changed == 0 {
      print k ": \"" v "\""
      changed=1
      next
    }
    { print }
  ' "$file" >"$tmp"
  mv "$tmp" "$file"
}

bump_version() {
  local current="$1"
  local kind="$2"
  local major minor patch
  IFS='.' read -r major minor patch <<<"$current"
  [[ "$major" =~ ^[0-9]+$ && "$minor" =~ ^[0-9]+$ && "$patch" =~ ^[0-9]+$ ]] \
    || die "Invalid semantic version: $current"

  case "$kind" in
    patch) patch=$((patch + 1)) ;;
    minor) minor=$((minor + 1)); patch=0 ;;
    major) major=$((major + 1)); minor=0; patch=0 ;;
    *) die "Version type must be patch, minor, or major" ;;
  esac

  printf '%s.%s.%s\n' "$major" "$minor" "$patch"
}

artifact_id_for() {
  local path="$1"
  local id
  id="$(frontmatter_value "$path" artifact_id || true)"
  if [[ -z "$id" && -f "$REGISTRY" ]]; then
    id="$(awk -F'\t' -v p="$path" 'NR > 1 && $2 == p {print $1; exit}' "$REGISTRY")"
  fi
  printf '%s\n' "${id:-UNREGISTERED}"
}

snapshot_path_for() {
  local path="$1"
  local version="$2"
  local noext="${path%.*}"
  local ext="${path##*.}"
  printf '.eos/history/%s/v%s.%s\n' "$noext" "$version" "$ext"
}

cmd_status() {
  printf '\nEOS WORKFLOW\n'
  printf '%-8s %-12s %-16s %-10s %s\n' "ORDER" "STAGE" "PHASE" "STATUS" "OUTPUT"
  awk -F'\t' 'NR > 1 {
    printf "%-8s %-12s %-16s %-10s %s\n", $1, $2, $3, $8, $4
  }' "$WORKFLOW"

  printf '\nNEXT\n'
  awk -F'\t' 'NR > 1 && $8 != "COMPLETE" {
    printf "%s — %s — %s\n", $2, $3, $4
    exit
  }' "$WORKFLOW"

  if command -v git >/dev/null 2>&1 && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    printf '\nGIT\n'
    git status --short
    [[ -n "$(git status --short)" ]] || printf 'clean\n'
  fi
}

cmd_next() {
  local row
  row="$(awk -F'\t' 'NR > 1 && $8 != "COMPLETE" {print; exit}' "$WORKFLOW")"
  if [[ -z "$row" ]]; then
    printf 'All EOS bootstrap stages are complete.\n'
    return
  fi

  IFS=$'\t' read -r order stage phase output lead reviewer gate status completed <<<"$row"
  cat <<EOF
Stage:      $stage
Order:      $order
Phase:      $phase
Output:     $output
Lead:       $lead
Reviewer:   $reviewer
Gate:       $gate
Status:     $status

Render the stage prompt with:

  ./scripts/eos prompt $stage
EOF
}

cmd_prompt() {
  local stage="${1:-}"
  [[ -n "$stage" ]] || die "prompt requires a stage such as EOSB-001"

  local prompt=".eos/prompts/${stage}.md"
  [[ -f "$prompt" ]] || die "No prompt registered for $stage"

  local row
  row="$(awk -F'\t' -v s="$stage" 'NR > 1 && $2 == s {print; exit}' "$WORKFLOW")"
  [[ -n "$row" ]] || die "Stage not found: $stage"

  IFS=$'\t' read -r order _ phase output lead reviewer gate status completed <<<"$row"

  cat <<EOF
# Engineering Operating System Task — $stage

You are operating inside a governed software-engineering repository.

## Responsibility Model

- Human: final authority and gate approval.
- ChatGPT: reasoning, synthesis, artifact drafting, consistency, traceability,
  architecture and planning review.
- Codex: bounded repository-local implementation and validation only after
  authorization.
- GitHub: canonical remote history, PR review, CI, issues, milestones, and
  integration record.

## Current Stage

- Phase: $phase
- Primary output: $output
- Lead: $lead
- Reviewer: $reviewer
- Gate: $gate
- Current status: $status

## Stage Instruction

EOF
  cat "$prompt"

  cat <<'EOF'

## Governing Rules

1. Read idea.md first.
2. Respect accepted higher-authority artifacts.
3. Surface contradictions instead of silently choosing one side.
4. Do not invent implementation decisions unless the stage explicitly requires
   them.
5. Preserve stable identifiers.
6. Update the designated artifacts completely, not as empty stubs.
7. Preserve traceability to source goals, requirements, constraints, ADRs, and
   specifications.
8. Mark unresolved uncertainty explicitly.
9. Recommend decisions; do not impersonate human approval.
10. When an accepted governed artifact materially changes, use the EOS
    versioning mechanism and record why.

## Primary Inception Source

EOF
  cat idea.md
}

update_stage_status() {
  local stage="$1"
  local new_status="$2"
  local completed_at="$3"
  local tmp
  tmp="$(mktemp)"
  awk -F'\t' -v OFS='\t' -v s="$stage" -v st="$new_status" -v ts="$completed_at" '
    NR == 1 { print; next }
    $2 == s { $8=st; $9=ts; found=1 }
    { print }
    END { if (!found) exit 42 }
  ' "$WORKFLOW" >"$tmp" || {
    rm -f "$tmp"
    die "Stage not found: $stage"
  }
  mv "$tmp" "$WORKFLOW"
}

cmd_complete() {
  local stage="${1:-}"
  [[ -n "$stage" ]] || die "complete requires a stage"
  update_stage_status "$stage" "COMPLETE" "$(now_iso)"
  printf 'Marked %s COMPLETE.\n' "$stage"
  printf 'Consider checkpointing the resulting coherent state:\n'
  printf '  ./scripts/eos checkpoint "complete %s"\n' "$stage"
}

cmd_reopen() {
  local stage="${1:-}"
  [[ -n "$stage" ]] || die "reopen requires a stage"
  update_stage_status "$stage" "PENDING" "-"
  printf 'Reopened %s.\n' "$stage"
}

cmd_version() {
  local path="${1:-}"
  local kind="${2:-}"
  shift 2 || true
  local message="${*:-}"

  [[ -n "$path" && -f "$path" ]] || die "Artifact file not found: $path"
  [[ -n "$kind" ]] || die "Specify patch, minor, or major"
  [[ -n "$message" ]] || die "A change message is required"

  local current id next snapshot ts
  current="$(frontmatter_value "$path" version)"
  [[ -n "$current" ]] || die "$path has no governed artifact version"
  id="$(artifact_id_for "$path")"
  next="$(bump_version "$current" "$kind")"
  snapshot="$(snapshot_path_for "$path" "$current")"
  ts="$(now_iso)"

  if [[ ! -e "$snapshot" ]]; then
    mkdir -p "$(dirname "$snapshot")"
    cp "$path" "$snapshot"
  fi

  replace_frontmatter_value "$path" version "$next"
  replace_frontmatter_value "$path" updated "${ts%%T*}"

  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$ts" "$id" "$path" "$current" "$next" "$kind" "$message" >>"$CHANGELOG"

  printf '%s: %s -> %s (%s)\n' "$path" "$current" "$next" "$message"
}

cmd_history() {
  local path="${1:-}"
  [[ -n "$path" ]] || die "history requires an artifact path"

  local id
  id="$(artifact_id_for "$path")"
  printf 'Artifact: %s\nPath: %s\n\n' "$id" "$path"

  printf 'Semantic artifact history:\n'
  awk -F'\t' -v p="$path" '
    NR > 1 && $3 == p {
      printf "  %s  %s -> %s  %-6s  %s\n", $1, $4, $5, $6, $7
    }
  ' "$CHANGELOG"

  printf '\nRetained snapshots:\n'
  local base=".eos/history/${path%.*}"
  if [[ -d "$base" ]]; then
    find "$base" -maxdepth 1 -type f -print | sort | sed 's/^/  /'
  else
    printf '  none yet\n'
  fi

  if command -v git >/dev/null 2>&1 && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    printf '\nGit history:\n'
    git log --oneline --follow -- "$path" 2>/dev/null | sed 's/^/  /' || true
  fi
}

cmd_rollback() {
  local path="${1:-}"
  local target="${2:-}"
  shift 2 || true
  local message="${*:-}"

  [[ -f "$path" ]] || die "Current artifact not found: $path"
  [[ -n "$target" ]] || die "rollback requires a target version"
  [[ -n "$message" ]] || die "rollback requires a message"

  target="${target#v}"

  local current current_snapshot target_snapshot id next ts tmp
  current="$(frontmatter_value "$path" version)"
  [[ -n "$current" ]] || die "$path is not a governed versioned artifact"

  current_snapshot="$(snapshot_path_for "$path" "$current")"
  target_snapshot="$(snapshot_path_for "$path" "$target")"
  [[ -f "$target_snapshot" ]] || die "No retained snapshot for version $target"

  mkdir -p "$(dirname "$current_snapshot")"
  [[ -e "$current_snapshot" ]] || cp "$path" "$current_snapshot"

  next="$(bump_version "$current" patch)"
  id="$(artifact_id_for "$path")"
  ts="$(now_iso)"
  tmp="$(mktemp)"
  cp "$target_snapshot" "$tmp"
  mv "$tmp" "$path"

  replace_frontmatter_value "$path" version "$next"
  replace_frontmatter_value "$path" updated "${ts%%T*}"

  printf '%s\t%s\t%s\t%s\t%s\trollback\tRESTORE v%s: %s\n' \
    "$ts" "$id" "$path" "$current" "$next" "$target" "$message" >>"$CHANGELOG"

  printf 'Restored %s content from v%s as new version v%s.\n' "$path" "$target" "$next"
}

cmd_checkpoint() {
  local message="${*:-}"
  [[ -n "$message" ]] || die "checkpoint requires a message"
  command -v git >/dev/null 2>&1 || die "git is required for checkpoints"
  git rev-parse --is-inside-work-tree >/dev/null 2>&1 || die "Not inside a Git repository"

  local ts tag meta
  ts="$(date -u +"%Y%m%dT%H%M%SZ")"
  tag="eos/checkpoint-$ts"
  meta=".eos/checkpoints/$ts.txt"

  mkdir -p .eos/checkpoints
  {
    printf 'timestamp=%s\n' "$(now_iso)"
    printf 'message=%s\n' "$message"
  } >"$meta"

  git add -A

  if git diff --cached --quiet; then
    warn "No changes to commit; creating no checkpoint."
    rm -f "$meta"
    return
  fi

  git commit -m "checkpoint: $message"
  git tag -a "$tag" -m "$message"
  printf 'Created checkpoint %s at %s\n' "$tag" "$(git rev-parse --short HEAD)"
}

cmd_verify() {
  local failures=0

  [[ -f idea.md ]] || { printf 'FAIL missing idea.md\n'; failures=$((failures+1)); }
  [[ -f "$WORKFLOW" ]] || { printf 'FAIL missing %s\n' "$WORKFLOW"; failures=$((failures+1)); }
  [[ -f "$REGISTRY" ]] || { printf 'FAIL missing %s\n' "$REGISTRY"; failures=$((failures+1)); }

  printf 'Checking registered artifacts...\n'
  while IFS=$'\t' read -r id path type authority; do
    [[ "$id" == "artifact_id" ]] && continue
    if [[ ! -f "$path" ]]; then
      printf 'FAIL %-24s missing %s\n' "$id" "$path"
      failures=$((failures+1))
      continue
    fi

    local fm_id
    fm_id="$(frontmatter_value "$path" artifact_id || true)"
    if [[ -n "$fm_id" && "$fm_id" != "$id" ]]; then
      printf 'FAIL %-24s frontmatter id is %s in %s\n' "$id" "$fm_id" "$path"
      failures=$((failures+1))
    else
      printf 'OK   %-24s %s\n' "$id" "$path"
    fi
  done <"$REGISTRY"

  printf '\nChecking duplicate artifact IDs...\n'
  local dupes
  dupes="$(tail -n +2 "$REGISTRY" | cut -f1 | sort | uniq -d)"
  if [[ -n "$dupes" ]]; then
    printf 'FAIL duplicate artifact IDs:\n%s\n' "$dupes"
    failures=$((failures+1))
  else
    printf 'OK   no duplicate registered artifact IDs\n'
  fi

  printf '\nChecking workflow stage uniqueness...\n'
  dupes="$(tail -n +2 "$WORKFLOW" | cut -f2 | sort | uniq -d)"
  if [[ -n "$dupes" ]]; then
    printf 'FAIL duplicate workflow stages:\n%s\n' "$dupes"
    failures=$((failures+1))
  else
    printf 'OK   workflow stage IDs unique\n'
  fi

  if (( failures > 0 )); then
    printf '\nVerification FAILED with %d issue(s).\n' "$failures"
    exit 1
  fi

  printf '\nVerification PASSED.\n'
}

cmd_responsibilities() {
  cat governance/responsibility-model.md
}

cmd="${1:-}"
shift || true

case "$cmd" in
  status) cmd_status "$@" ;;
  next) cmd_next "$@" ;;
  prompt) cmd_prompt "$@" ;;
  complete) cmd_complete "$@" ;;
  reopen) cmd_reopen "$@" ;;
  version) cmd_version "$@" ;;
  history) cmd_history "$@" ;;
  rollback) cmd_rollback "$@" ;;
  checkpoint) cmd_checkpoint "$@" ;;
  verify) cmd_verify "$@" ;;
  responsibilities) cmd_responsibilities "$@" ;;
  -h|--help|help|"") usage ;;
  *) die "Unknown command: $cmd" ;;
esac
