#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import datetime as dt
import fnmatch
import hashlib
import json
import os
import platform
import re
import shutil
import socket
import subprocess
import sys
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Iterable

UTC = dt.timezone.utc
EXEC_FIELDS = [
    "id", "path", "target", "status", "branch", "worktree", "baseline_commit",
    "governing_hash", "contract_hash", "result_path", "actor", "created", "updated",
]
ACTIVE_EXEC_STATES = {"PREPARED", "RUNNING", "RESULT_INGESTED", "VERIFIED", "BLOCKED"}
TERMINAL_EXEC_STATES = {"CLOSED", "ABORTED", "FAILED", "INVALIDATED"}
SYSTEM_FORBIDDEN_DEFAULT = [".git", ".git/**", ".eos", ".eos/**"]
GOVERNED_DEFAULT = [
    "idea.md", "vision/**", "product/**", "architecture/**", "specifications/**",
    "governance/**", "engineering/increments/**", "engineering/work-cycles/**",
    "engineering/work-packets/**",
]


class EoseError(RuntimeError):
    pass


def now_iso() -> str:
    return dt.datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run(args: list[str], *, cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=check)


def discover_root() -> Path:
    explicit = os.environ.get("EOS_ROOT", "").strip()
    if explicit:
        return Path(explicit).resolve()
    candidate = Path(__file__).resolve().parents[2]
    if (candidate / ".eos").exists():
        return candidate
    try:
        return Path(run(["git", "rev-parse", "--show-toplevel"]).stdout.strip()).resolve()
    except Exception:
        return candidate


ROOT = discover_root()
EOS = ROOT / ".eos"
REGISTRY = EOS / "executions.tsv"
EVENTS = EOS / "events.jsonl"
POLICY = EOS / "execution-policy.json"
LOCKS = EOS / "locks"
EXEC_DIR = EOS / "executions"
CONTRACTS = EOS / "contracts"
EVIDENCE = EOS / "evidence"
CORE = ROOT / "tools" / "eos" / "eos.py"


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def actor_name(explicit: str = "") -> str:
    return explicit or os.environ.get("EOS_ACTOR") or os.environ.get("USER") or "unknown"


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def write_tsv(path: Path, fields: list[str], rows: Iterable[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})
        f.flush()
        os.fsync(f.fileno())
    tmp.replace(path)


def rows() -> list[dict[str, str]]:
    return read_tsv(REGISTRY)


def find_exec(exec_id: str) -> dict[str, str]:
    for row in rows():
        if row.get("id") == exec_id:
            return row
    raise EoseError(f"Unknown execution session: {exec_id}")


def update_exec(exec_id: str, **updates: str) -> dict[str, str]:
    all_rows = rows()
    for row in all_rows:
        if row.get("id") == exec_id:
            row.update(updates)
            row["updated"] = now_iso()
            write_tsv(REGISTRY, EXEC_FIELDS, all_rows)
            sync_session_json(row)
            return row
    raise EoseError(f"Unknown execution session: {exec_id}")


def append_event(event_type: str, *, target: str = "", action: str = "", from_state: str = "", to_state: str = "", actor: str = "", reason: str = "", metadata: dict | None = None) -> None:
    event = {
        "event_id": "EVT-" + uuid.uuid4().hex.upper(),
        "schema_version": "1.0.0",
        "timestamp": now_iso(),
        "event_type": event_type,
        "actor": actor_name(actor),
        "target": target,
        "entity_kind": "EXEC" if target.startswith("EXEC-") else "",
        "action": action,
        "from_state": from_state,
        "to_state": to_state,
        "reason": reason,
        "commit": git_head(ROOT),
        "metadata": metadata or {},
    }
    EVENTS.parent.mkdir(parents=True, exist_ok=True)
    with EVENTS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n")
        f.flush()
        os.fsync(f.fileno())


def load_json(path: Path, default: dict | None = None) -> dict:
    if not path.exists():
        if default is not None:
            return dict(default)
        raise EoseError(f"Missing {rel(path)}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise EoseError(f"Invalid JSON in {rel(path)}: {exc}") from exc
    if not isinstance(value, dict):
        raise EoseError(f"Expected object in {rel(path)}")
    return value


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def governing_content_hash(path: Path) -> str:
    """Hash semantic governed content while ignoring operational lifecycle metadata."""
    if path.suffix.lower() != ".md":
        return sha256_file(path)
    text = path.read_text(encoding="utf-8", errors="strict")
    lines = text.splitlines()
    normalized: list[str] = []
    in_frontmatter = bool(lines and lines[0].strip() == "---")
    frontmatter_closed = not in_frontmatter
    for i, line in enumerate(lines):
        if in_frontmatter and i == 0:
            normalized.append(line); continue
        if in_frontmatter and not frontmatter_closed:
            if line.strip() == "---":
                frontmatter_closed = True; normalized.append(line); continue
            if re.match(r"^(status|updated):\s*", line):
                continue
            normalized.append(line); continue
        if re.match(r"^\*\*State:\*\*\s*", line):
            continue
        normalized.append(line)
    return sha256_bytes(("\n".join(normalized).rstrip() + "\n").encode("utf-8"))


def git_head(cwd: Path) -> str:
    try:
        return run(["git", "rev-parse", "HEAD"], cwd=cwd).stdout.strip()
    except Exception:
        return ""


def git_branch(cwd: Path) -> str:
    try:
        return run(["git", "branch", "--show-current"], cwd=cwd).stdout.strip()
    except Exception:
        return ""


def git_status(cwd: Path) -> str:
    try:
        return run(["git", "status", "--porcelain"], cwd=cwd).stdout
    except Exception:
        return ""


def non_eos_dirty_paths(cwd: Path) -> list[str]:
    dirty: list[str] = []
    for line in git_status(cwd).splitlines():
        if len(line) < 4:
            continue
        raw = line[3:].strip()
        # Rename status uses `old -> new`; inspect the destination path.
        path = raw.split(" -> ")[-1]
        if path == ".eos" or path.startswith(".eos/"):
            continue
        dirty.append(path)
    return sorted(set(dirty))


def core(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["EOS_ROOT"] = str(ROOT)
    return subprocess.run([sys.executable, str(CORE), *args], cwd=ROOT, env=env, text=True, capture_output=True, check=check)


def wp_row(target: str) -> dict[str, str]:
    for row in read_tsv(EOS / "work-packets.tsv"):
        if row.get("id") == target:
            return row
    raise EoseError(f"Unknown work packet: {target}")


def artifact_registry() -> list[dict[str, str]]:
    return read_tsv(EOS / "artifacts.tsv")


def artifact_path_for_id(target: str) -> Path | None:
    for table in ("program-increments.tsv", "work-cycles.tsv", "work-packets.tsv", "change-requests.tsv", "maintenance.tsv", "releases.tsv"):
        for row in read_tsv(EOS / table):
            if row.get("id") == target and row.get("path"):
                p = ROOT / row["path"]
                if p.exists():
                    return p
    for row in artifact_registry():
        if row.get("artifact_id") == target and row.get("path"):
            p = ROOT / row["path"]
            if p.exists():
                return p
    return None


ID_RE = re.compile(r"\b(?:REQ-[A-Z0-9][A-Z0-9-]*|CAP-[A-Z0-9][A-Z0-9-]*|QA-[A-Z0-9][A-Z0-9-]*|ADR-\d{4}|SPEC-[A-Z0-9][A-Z0-9-]*|PI-\d{3}|WC-\d{4}|WP(?:-[A-Z][A-Z0-9]*)?-\d{4}|RISK-\d{3,4})\b")


def referenced_ids(path: Path) -> list[str]:
    if not path.exists():
        return []
    own = ""
    text = path.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r'^artifact_id:\s*["\']?([^"\'\n]+)', text, flags=re.M)
    if m:
        own = m.group(1).strip()
    return sorted(x for x in set(ID_RE.findall(text)) if x != own)


def governing_paths(target: str) -> list[Path]:
    wp = wp_row(target)
    wp_path = ROOT / wp["path"]
    ids = set(referenced_ids(wp_path))
    for parent_key in ("pi", "wc"):
        if wp.get(parent_key):
            ids.add(wp[parent_key])
    paths: set[Path] = {wp_path}
    for rid in ids:
        p = artifact_path_for_id(rid)
        if p and p.exists():
            paths.add(p)
    return sorted(paths, key=lambda p: rel(p))


def governing_manifest(target: str, *, root: Path = ROOT) -> list[dict[str, str]]:
    manifest: list[dict[str, str]] = []
    for source in governing_paths(target):
        rp = rel(source)
        p = root / rp
        if not p.exists():
            manifest.append({"path": rp, "sha256": "MISSING"})
        else:
            manifest.append({"path": rp, "sha256": governing_content_hash(p)})
    return manifest


def manifest_hash(manifest: list[dict[str, str]]) -> str:
    return sha256_bytes(canonical_bytes(manifest))


def execution_policy() -> dict:
    default = {
        "branch_prefix": "wp/",
        "worktree_root": f"../.{ROOT.name}-worktrees",
        "require_clean_current_tree_for_no_worktree": True,
        "system_forbidden_paths": SYSTEM_FORBIDDEN_DEFAULT,
        "governed_paths": GOVERNED_DEFAULT,
    }
    value = load_json(POLICY, default)
    for k, v in default.items():
        value.setdefault(k, v)
    return value


def scope_directives(target: str) -> dict[str, list[str]]:
    path = ROOT / wp_row(target)["path"]
    text = path.read_text(encoding="utf-8", errors="ignore")
    out = {"allowed": [], "forbidden": [], "allowed_governed": []}
    patterns = {
        "allowed-path": "allowed",
        "forbidden-path": "forbidden",
        "allowed-governed-path": "allowed_governed",
    }
    for raw in text.splitlines():
        m = re.match(r"^\s*-\s*(allowed-path|forbidden-path|allowed-governed-path):\s*`?([^`#]+?)`?\s*$", raw)
        if m:
            out[patterns[m.group(1)]].append(m.group(2).strip())
    if not out["allowed"]:
        out["allowed"] = ["*", "**/*"]
    return out


def normalize_repo_path(path: str) -> str:
    return path[2:] if path.startswith("./") else path


def path_matches(path: str, patterns: list[str]) -> bool:
    normalized = normalize_repo_path(path)
    return any(fnmatch.fnmatchcase(normalized, normalize_repo_path(p)) for p in patterns)


def scope_check(target: str, changed_files: list[str]) -> dict:
    directives = scope_directives(target)
    policy = execution_policy()
    system_forbidden = list(policy.get("system_forbidden_paths", SYSTEM_FORBIDDEN_DEFAULT))
    governed = list(policy.get("governed_paths", GOVERNED_DEFAULT))
    violations: list[dict[str, str]] = []
    for raw in sorted(set(changed_files)):
        path = normalize_repo_path(raw)
        if path_matches(path, system_forbidden):
            violations.append({"path": path, "reason": "EOS/Git internal path is never implementation scope"})
            continue
        if not path_matches(path, directives["allowed"]):
            violations.append({"path": path, "reason": "not matched by any allowed-path directive"})
            continue
        if path_matches(path, directives["forbidden"]):
            violations.append({"path": path, "reason": "matched forbidden-path directive"})
            continue
        if path_matches(path, governed) and not path_matches(path, directives["allowed_governed"]):
            violations.append({"path": path, "reason": "governed artifact changed without allowed-governed-path authorization"})
    return {"passed": not violations, "directives": directives, "violations": violations}


def branch_for(target: str) -> str:
    prefix = str(execution_policy().get("branch_prefix", "wp/"))
    suffix = target.removeprefix("WP-").lower().replace("_", "-")
    return prefix + suffix


def worktree_root() -> Path:
    raw = str(execution_policy().get("worktree_root", f"../.{ROOT.name}-worktrees"))
    raw = raw.replace("{repo}", ROOT.name)
    p = Path(raw).expanduser()
    if not p.is_absolute():
        p = (ROOT / p).resolve()
    return p


def worktree_for(target: str) -> Path:
    return worktree_root() / target.lower()


def git_worktrees() -> list[dict[str, str]]:
    try:
        raw = run(["git", "worktree", "list", "--porcelain"], cwd=ROOT).stdout
    except Exception:
        return []
    out: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for line in raw.splitlines() + [""]:
        if not line:
            if current:
                out.append(current)
                current = {}
            continue
        key, _, value = line.partition(" ")
        current[key] = value
    return out


def create_worktree(target: str, *, base: str = "HEAD", custom_path: str = "") -> tuple[str, Path]:
    branch = branch_for(target)
    path = Path(custom_path).expanduser().resolve() if custom_path else worktree_for(target)
    if path.exists() and any(Path(w.get("worktree", "")).resolve() == path for w in git_worktrees() if w.get("worktree")):
        return branch, path
    if path.exists() and any(path.iterdir()):
        raise EoseError(f"Worktree destination is not empty: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    branch_exists = run(["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"], cwd=ROOT, check=False).returncode == 0
    base_commit = run(["git", "rev-parse", "--verify", f"{base}^{{commit}}"], cwd=ROOT).stdout.strip()
    if branch_exists:
        branch_head = run(["git", "rev-parse", branch], cwd=ROOT).stdout.strip()
        if branch_head != base_commit:
            already_integrated = run(["git", "merge-base", "--is-ancestor", branch_head, base_commit], cwd=ROOT, check=False).returncode == 0
            if not already_integrated:
                raise EoseError(f"Existing execution branch {branch} contains unmerged/divergent work ({branch_head}); refusing to reset it to {base_commit}")
            run(["git", "branch", "-f", branch, base_commit], cwd=ROOT)
        run(["git", "worktree", "add", str(path), branch], cwd=ROOT)
    else:
        run(["git", "worktree", "add", "-b", branch, str(path), base_commit], cwd=ROOT)
    append_event("WORKTREE_CREATED", target=target, action="worktree-create", reason="isolated execution worktree created", metadata={"branch": branch, "worktree": str(path), "base": base})
    return branch, path


def remove_worktree(target: str, *, force: bool = False) -> None:
    active = active_exec_for(target)
    if active and not force:
        raise EoseError(f"Cannot remove worktree while active execution exists: {', '.join(r['id'] for r in active)}")
    candidates = [r for r in rows() if r.get("target") == target and r.get("worktree")]
    path = Path(candidates[-1]["worktree"]) if candidates else worktree_for(target)
    if path.exists():
        args = ["git", "worktree", "remove"]
        if force:
            args.append("--force")
        args.append(str(path))
        run(args, cwd=ROOT)
        append_event("WORKTREE_REMOVED", target=target, action="worktree-remove", reason="execution worktree removed", metadata={"worktree": str(path), "force": force})


def process_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


@contextmanager
def target_lock(target: str, action: str):
    LOCKS.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", target)
    path = LOCKS / f"{safe}.lock.json"
    payload = {"target": target, "action": action, "pid": os.getpid(), "host": socket.gethostname(), "actor": actor_name(), "created": now_iso()}
    fd = None
    for attempt in range(2):
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            break
        except FileExistsError:
            try:
                existing = load_json(path)
            except Exception:
                existing = {}
            if attempt == 0 and existing.get("host") == socket.gethostname() and not process_alive(int(existing.get("pid", 0) or 0)):
                path.unlink(missing_ok=True)
                continue
            raise EoseError(f"Concurrent EOS mutation lock exists for {target}: {path} ({existing})")
    assert fd is not None
    try:
        os.write(fd, canonical_bytes(payload))
        os.fsync(fd)
        os.close(fd)
        fd = None
        yield
    finally:
        if fd is not None:
            os.close(fd)
        path.unlink(missing_ok=True)


def stale_for(target: str) -> list[dict[str, str]]:
    return [r for r in read_tsv(EOS / "stale.tsv") if r.get("target") == target and r.get("status") == "OPEN"]


def active_exec_for(target: str) -> list[dict[str, str]]:
    return [r for r in rows() if r.get("target") == target and r.get("status") in ACTIVE_EXEC_STATES]


def preflight(target: str, *, no_worktree: bool = False, base: str = "HEAD") -> dict:
    checks: list[dict[str, object]] = []
    try:
        wp = wp_row(target)
        checks.append({"check": "work_packet_registered", "passed": True, "detail": wp.get("path", "")})
    except EoseError as exc:
        return {"target": target, "passed": False, "checks": [{"check": "work_packet_registered", "passed": False, "detail": str(exc)}]}
    checks.append({"check": "state_authorized", "passed": wp.get("status") in {"AUTHORIZED", "IN_PROGRESS"}, "detail": wp.get("status", "")})
    git_ok = (ROOT / ".git").exists() or run(["git", "rev-parse", "--git-dir"], cwd=ROOT, check=False).returncode == 0
    checks.append({"check": "git_repository", "passed": git_ok, "detail": str(ROOT)})
    head = git_head(ROOT)
    checks.append({"check": "baseline_commit", "passed": bool(head), "detail": head or "no HEAD commit"})
    dirty = non_eos_dirty_paths(ROOT)
    governing_rel = {item["path"] for item in governing_manifest(target)}
    dirty_governing = sorted(set(dirty) & governing_rel)
    other_dirty = sorted(set(dirty) - governing_rel)
    checks.append({"check": "governing_baseline_committed", "passed": not dirty_governing, "detail": ", ".join(dirty_governing) or "all governing inputs committed"})
    checks.append({"check": "other_uncommitted_project_state", "passed": True, "detail": ("warning: not included in isolated worktree baseline: " + ", ".join(other_dirty)) if other_dirty else "none"})
    stale = stale_for(target)
    checks.append({"check": "no_open_stale_dependencies", "passed": not stale, "detail": ", ".join(r.get("id", "") for r in stale) or "none"})
    active = active_exec_for(target)
    checks.append({"check": "single_active_execution", "passed": not active, "detail": ", ".join(r.get("id", "") for r in active) or "none"})
    gov = governing_manifest(target)
    missing = [x["path"] for x in gov if x["sha256"] == "MISSING"]
    checks.append({"check": "governing_inputs_present", "passed": not missing, "detail": ", ".join(missing) or f"{len(gov)} input(s)"})
    base_proc = run(["git", "rev-parse", "--verify", f"{base}^{{commit}}"], cwd=ROOT, check=False)
    base_ok = base_proc.returncode == 0
    base_commit = base_proc.stdout.strip() if base_ok else ""
    checks.append({"check": "base_ref_resolves", "passed": base_ok, "detail": f"{base} -> {base_commit}" if base_ok else base})
    if no_worktree:
        clean = not bool(git_status(ROOT).strip())
        required = bool(execution_policy().get("require_clean_current_tree_for_no_worktree", True))
        checks.append({"check": "current_tree_clean", "passed": clean or not required, "detail": "clean" if clean else "dirty"})
    else:
        path = worktree_for(target)
        linked = next((w for w in git_worktrees() if w.get("worktree") and Path(w["worktree"]).resolve() == path.resolve()), None)
        if linked:
            wt_clean = not bool(git_status(path).strip())
            wt_head = git_head(path)
            wt_branch = git_branch(path)
            expected_branch = branch_for(target)
            reusable = wt_clean and base_ok and wt_head == base_commit and wt_branch == expected_branch
            detail = f"{path}; branch={wt_branch}; head={wt_head}; clean={wt_clean}; expected_branch={expected_branch}; expected_head={base_commit}"
            checks.append({"check": "existing_worktree_reusable", "passed": reusable, "detail": detail})
        else:
            conflict = path.exists() and any(path.iterdir())
            checks.append({"check": "worktree_destination_available", "passed": not conflict, "detail": str(path)})
            expected_branch = branch_for(target)
            branch_exists = run(["git", "show-ref", "--verify", "--quiet", f"refs/heads/{expected_branch}"], cwd=ROOT, check=False).returncode == 0
            if branch_exists and base_ok:
                branch_head = run(["git", "rev-parse", expected_branch], cwd=ROOT).stdout.strip()
                integrated = branch_head == base_commit or run(["git", "merge-base", "--is-ancestor", branch_head, base_commit], cwd=ROOT, check=False).returncode == 0
                checks.append({"check": "existing_branch_safe_to_reuse", "passed": integrated, "detail": f"branch={expected_branch}; branch_head={branch_head}; base={base_commit}; integrated={integrated}"})
    return {"target": target, "passed": all(bool(c["passed"]) for c in checks), "checks": checks, "governing_hash": manifest_hash(gov), "governing_inputs": gov}


def format_preflight(report: dict) -> str:
    lines = [f"EOSE PREFLIGHT — {report['target']}", ""]
    for c in report["checks"]:
        lines.append(f"{'PASS' if c['passed'] else 'FAIL':<4}  {c['check']:<34} {c['detail']}")
    lines += ["", f"RESULT: {'PASS' if report['passed'] else 'FAIL'}"]
    return "\n".join(lines)


def next_exec_id() -> str:
    nums = []
    for row in rows():
        m = re.fullmatch(r"EXEC-(\d{4})", row.get("id", ""))
        if m:
            nums.append(int(m.group(1)))
    return f"EXEC-{max(nums, default=0) + 1:04d}"


def environment_snapshot(cwd: Path) -> dict:
    tools: dict[str, str] = {}
    candidates = [
        ("git", ["git", "--version"]), ("python3", ["python3", "--version"]),
        ("bash", ["bash", "--version"]), ("node", ["node", "--version"]),
        ("bun", ["bun", "--version"]), ("go", ["go", "version"]),
        ("rustc", ["rustc", "--version"]), ("cargo", ["cargo", "--version"]),
    ]
    for name, cmd in candidates:
        if not shutil.which(cmd[0]):
            continue
        try:
            p = run(cmd, cwd=cwd, check=False)
            line = (p.stdout or p.stderr).splitlines()[0] if (p.stdout or p.stderr).splitlines() else ""
            tools[name] = line[:500]
        except Exception:
            continue
    custom: list[dict[str, object]] = []
    config = EOS / "environment.commands"
    if config.exists():
        for raw in config.read_text(encoding="utf-8").splitlines():
            cmd = raw.strip()
            if not cmd or cmd.startswith("#"):
                continue
            # Environment capture is intentionally shell-based only for user-authored
            # local commands, never values produced by an agent/result file.
            p = subprocess.run(["bash", "-lc", cmd], cwd=cwd, text=True, capture_output=True)
            custom.append({"command": cmd, "exit_code": p.returncode, "output": (p.stdout + p.stderr)[:4000]})
    locks: list[dict[str, str]] = []
    names = {"bun.lock", "bun.lockb", "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "Cargo.lock", "go.sum", "uv.lock", "poetry.lock", "Pipfile.lock"}
    for p in cwd.iterdir():
        if p.is_file() and (p.name in names or p.name.startswith("requirements") and p.suffix == ".txt"):
            locks.append({"path": p.name, "sha256": sha256_file(p)})
    return {
        "captured": now_iso(), "host": socket.gethostname(), "platform": platform.platform(),
        "python": sys.version.splitlines()[0], "shell": os.environ.get("SHELL", ""),
        "branch": git_branch(cwd), "head": git_head(cwd), "tools": tools,
        "lockfiles": sorted(locks, key=lambda x: x["path"]), "custom": custom,
    }


def contract_payload(exec_id: str, target: str, branch: str, worktree: Path, baseline: str, actor: str) -> dict:
    manifest = governing_manifest(target, root=worktree)
    payload = {
        "schema_version": "2.0.0",
        "execution_id": exec_id,
        "target": target,
        "generated": now_iso(),
        "actor": actor_name(actor),
        "repository": str(ROOT),
        "branch": branch,
        "worktree": str(worktree),
        "baseline_commit": baseline,
        "governing_inputs": manifest,
        "governing_hash": manifest_hash(manifest),
        "scope": scope_directives(target),
        "system_forbidden_paths": list(execution_policy().get("system_forbidden_paths", SYSTEM_FORBIDDEN_DEFAULT)),
        "governed_paths": list(execution_policy().get("governed_paths", GOVERNED_DEFAULT)),
        "environment": environment_snapshot(worktree),
        "required_result_schema": {
            "execution_id": exec_id,
            "target": target,
            "status": "completed|blocked|failed",
            "summary": "string",
            "changed_files": ["path"],
            "validation": [{"command": "string", "exit_code": 0, "summary": "string"}],
            "acceptance_criteria": [{"criterion": "string", "status": "passed|failed|not-run", "evidence": "string"}],
            "risks": ["string"],
            "unresolved_issues": ["string"],
            "proposed_commit_message": "string"
        },
    }
    payload["contract_hash"] = sha256_bytes(canonical_bytes(payload))
    return payload


def markdown_contract(payload: dict) -> str:
    target = payload["target"]
    wp_path = ROOT / wp_row(target)["path"]
    lines = [
        f"# Codex Execution Contract v2 — {target}", "",
        f"Execution: {payload['execution_id']}", f"Generated: {payload['generated']}",
        f"Branch: `{payload['branch']}`", f"Worktree: `{payload['worktree']}`",
        f"Baseline: `{payload['baseline_commit']}`", f"Governing hash: `{payload['governing_hash']}`",
        f"Contract hash: `{payload['contract_hash']}`", "",
        "## Authority", "",
        "This contract authorizes bounded implementation only. It does not authorize changes to product/architecture/specification policy unless the work packet explicitly lists the exact governed path with `allowed-governed-path`.", "",
        "## Concurrency / Freshness", "",
        "Before finalizing work, verify this contract with `./scripts/eos contract verify " + payload['execution_id'] + "`. If governing inputs drift, stop: the execution contract is invalid.", "",
        "## Execution Scope", "",
    ]
    for p in payload["scope"]["allowed"]:
        lines.append(f"- allowed-path: `{p}`")
    for p in payload["scope"]["forbidden"]:
        lines.append(f"- forbidden-path: `{p}`")
    for p in payload["scope"]["allowed_governed"]:
        lines.append(f"- allowed-governed-path: `{p}`")
    lines += ["", "## Work Packet", "", wp_path.read_text(encoding="utf-8"), "", "## Governing Input Fingerprints", ""]
    for item in payload["governing_inputs"]:
        lines.append(f"- `{item['path']}` — `{item['sha256']}`")
    lines += [
        "", "## Required Operating Procedure", "",
        "1. Work only inside the assigned worktree and branch.",
        "2. Do not edit `.eos/` or Git internals.",
        "3. Do not expand product/architecture/specification scope to make implementation easier.",
        "4. Preserve stable IDs and traceability references.",
        "5. Run repository-prescribed validation and WP-specific validation.",
        "6. Compare actual Git changes against execution scope.",
        "7. Produce the structured JSON completion result described below.",
        "8. Stop and report BLOCKED if a governing decision must change.",
        "", "## Required Completion Result", "",
        f"Write JSON matching the contract to `.eos-result-{payload['execution_id']}.json` in the worktree, then ingest it from the main repository:", "",
        f"`./scripts/eos execution ingest {payload['execution_id']} <path-to-result.json>`", "",
        "The result is a claim. EOS independently compares it with the real Git diff and contract fingerprint.", "",
    ]
    return "\n".join(lines) + "\n"


def sync_session_json(row: dict[str, str]) -> None:
    path = ROOT / row["path"]
    existing = load_json(path, {}) if path.exists() else {}
    existing.setdefault("schema_version", "1.0.0")
    existing["registry"] = {k: row.get(k, "") for k in EXEC_FIELDS}
    tmp = path.with_suffix(".json.tmp")
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(json.dumps(existing, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def transition_exec(exec_id: str, new_state: str, *, action: str, reason: str = "", actor: str = "") -> dict[str, str]:
    row = find_exec(exec_id)
    machine = load_json(EOS / "state-machines" / "exec.json")
    current = row["status"]
    allowed = machine.get("transitions", {}).get(current, [])
    if new_state != current and new_state not in allowed:
        raise EoseError(f"Illegal EXEC transition {exec_id}: {current} -> {new_state}; allowed: {', '.join(allowed) or '(none)'}")
    append_event("STATE_TRANSITION", target=exec_id, action=action, from_state=current, to_state=new_state, actor=actor, reason=reason, metadata={"target_wp": row.get("target", "")})
    return update_exec(exec_id, status=new_state)


def create_session(target: str, *, no_worktree: bool = False, base: str = "HEAD", actor: str = "") -> tuple[dict[str, str], dict]:
    with target_lock(target, "execute"):
        report = preflight(target, no_worktree=no_worktree, base=base)
        if not report["passed"]:
            raise EoseError("Execution preflight failed:\n" + format_preflight(report))
        wp = wp_row(target)
        if wp["status"] == "AUTHORIZED":
            p = core("start", target, check=False)
            if p.returncode != 0:
                raise EoseError((p.stderr or p.stdout).strip())
        baseline = git_head(ROOT)
        if no_worktree:
            branch, wt = git_branch(ROOT), ROOT
        else:
            branch, wt = create_worktree(target, base=base)
        exec_id = next_exec_id()
        actor_v = actor_name(actor)
        payload = contract_payload(exec_id, target, branch, wt, baseline, actor_v)
        md_path = CONTRACTS / f"{exec_id}-{target}.codex.md"
        json_path = CONTRACTS / f"{exec_id}-{target}.codex.json"
        CONTRACTS.mkdir(parents=True, exist_ok=True)
        md_path.write_text(markdown_contract(payload), encoding="utf-8")
        json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        session_path = EXEC_DIR / f"{exec_id}.json"
        EXEC_DIR.mkdir(parents=True, exist_ok=True)
        session = {
            "schema_version": "1.0.0", "execution_id": exec_id, "target": target,
            "contract": {"markdown": rel(md_path), "json": rel(json_path), "hash": payload["contract_hash"]},
            "governing_inputs": payload["governing_inputs"], "scope": payload["scope"],
            "environment": payload["environment"], "created": now_iso(), "result": None,
        }
        session_path.write_text(json.dumps(session, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        row = {
            "id": exec_id, "path": rel(session_path), "target": target, "status": "PREPARED",
            "branch": branch, "worktree": str(wt), "baseline_commit": baseline,
            "governing_hash": payload["governing_hash"], "contract_hash": payload["contract_hash"],
            "result_path": "", "actor": actor_v, "created": now_iso(), "updated": now_iso(),
        }
        all_rows = rows(); all_rows.append(row); write_tsv(REGISTRY, EXEC_FIELDS, all_rows)
        append_event("ENTITY_CREATED", target=exec_id, action="prepare", to_state="PREPARED", actor=actor_v, reason="execution session prepared", metadata={"row": row, "wp": target})
        row = transition_exec(exec_id, "RUNNING", action="execute-start", reason="execution session started", actor=actor_v)
        return row, payload


def contract_for_exec(exec_id: str) -> tuple[dict[str, str], dict]:
    row = find_exec(exec_id)
    session = load_json(ROOT / row["path"])
    contract_path = ROOT / session["contract"]["json"]
    return row, load_json(contract_path)


def verify_contract(exec_id: str) -> dict:
    row, contract = contract_for_exec(exec_id)
    wt = Path(row["worktree"] or ROOT)
    checks: list[dict[str, object]] = []
    original_hash = contract.get("contract_hash", "")
    copy = dict(contract); copy.pop("contract_hash", None)
    calculated = sha256_bytes(canonical_bytes(copy))
    checks.append({"check": "contract_hash", "passed": calculated == original_hash == row.get("contract_hash"), "detail": f"expected={original_hash} calculated={calculated}"})
    worktree_manifest = []
    canonical_manifest = []
    for item in contract.get("governing_inputs", []):
        wp = wt / item["path"]
        cp = ROOT / item["path"]
        worktree_manifest.append({"path": item["path"], "sha256": governing_content_hash(wp) if wp.exists() else "MISSING"})
        canonical_manifest.append({"path": item["path"], "sha256": governing_content_hash(cp) if cp.exists() else "MISSING"})
    worktree_gov = manifest_hash(worktree_manifest)
    canonical_gov = manifest_hash(canonical_manifest)
    checks.append({"check": "worktree_governing_inputs_unchanged", "passed": worktree_manifest == contract.get("governing_inputs", []), "detail": f"expected={row.get('governing_hash','')} worktree={worktree_gov}"})
    checks.append({"check": "canonical_governing_inputs_unchanged", "passed": canonical_manifest == contract.get("governing_inputs", []), "detail": f"expected={row.get('governing_hash','')} canonical={canonical_gov}"})
    head = git_head(wt)
    base = row.get("baseline_commit", "")
    ancestor = bool(base) and run(["git", "merge-base", "--is-ancestor", base, head], cwd=wt, check=False).returncode == 0
    checks.append({"check": "baseline_is_ancestor", "passed": ancestor, "detail": f"baseline={base} head={head}"})
    branch_ok = git_branch(wt) == row.get("branch", "")
    checks.append({"check": "expected_branch", "passed": branch_ok, "detail": f"expected={row.get('branch','')} actual={git_branch(wt)}"})
    result = {"execution_id": exec_id, "target": row["target"], "passed": all(bool(c["passed"]) for c in checks), "checks": checks, "worktree_governing_hash": worktree_gov, "canonical_governing_hash": canonical_gov}
    if not result["passed"] and row["status"] not in TERMINAL_EXEC_STATES and row["status"] != "INVALIDATED":
        transition_exec(exec_id, "INVALIDATED", action="contract-verify", reason="contract freshness/concurrency invariant failed")
        append_event("EXECUTION_CONTRACT_INVALIDATED", target=exec_id, action="contract-verify", reason="execution contract no longer matches governing/baseline state", metadata=result)
    return result


def changed_files(row: dict[str, str]) -> list[str]:
    wt = Path(row["worktree"] or ROOT)
    base = row["baseline_commit"]
    p = run(["git", "diff", "--name-only", base, "--"], cwd=wt, check=False)
    values = {x.strip() for x in p.stdout.splitlines() if x.strip()}
    q = run(["git", "ls-files", "--others", "--exclude-standard"], cwd=wt, check=False)
    values.update(x.strip() for x in q.stdout.splitlines() if x.strip())
    # The structured agent result is an EOSE control artifact, not product work.
    # It is intentionally ignored by scope/diff checks when placed at worktree root.
    values = {v for v in values if not re.fullmatch(r"\.eos-result-EXEC-\d{4}\.json", v)}
    return sorted(values)


def validate_result(data: dict, exec_id: str, target: str) -> list[str]:
    errors: list[str] = []
    if data.get("execution_id") != exec_id: errors.append("execution_id mismatch")
    if data.get("target") != target: errors.append("target mismatch")
    if data.get("status") not in {"completed", "blocked", "failed"}: errors.append("status must be completed, blocked, or failed")
    if not isinstance(data.get("summary", ""), str): errors.append("summary must be a string")
    for key in ("changed_files", "validation", "acceptance_criteria", "risks", "unresolved_issues"):
        if key in data and not isinstance(data[key], list): errors.append(f"{key} must be a list")
    return errors


def ingest_result(exec_id: str, result_path: Path) -> dict:
    with target_lock(exec_id, "ingest"):
        row = find_exec(exec_id)
        if row["status"] != "RUNNING":
            raise EoseError(f"{exec_id} must be RUNNING to ingest a result; current={row['status']}")
        freshness = verify_contract(exec_id)
        if not freshness["passed"]:
            raise EoseError("Execution contract is invalid; result cannot be ingested")
        data = load_json(result_path)
        errors = validate_result(data, exec_id, row["target"])
        if errors:
            raise EoseError("Invalid execution result:\n- " + "\n- ".join(errors))
        actual = changed_files(row)
        declared = sorted(set(str(x) for x in data.get("changed_files", [])))
        scope = scope_check(row["target"], actual)
        comparison = {
            "actual_changed_files": actual, "declared_changed_files": declared,
            "undeclared_actual": sorted(set(actual) - set(declared)),
            "declared_but_not_actual": sorted(set(declared) - set(actual)),
            "scope": scope,
        }
        dest = EVIDENCE / f"{exec_id}-result.json"
        EVIDENCE.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps({"agent_result": data, "eos_observation": comparison, "ingested": now_iso()}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        session = load_json(ROOT / row["path"])
        session["result"] = {"path": rel(dest), "ingested": now_iso(), "agent_status": data["status"], "scope_passed": scope["passed"]}
        (ROOT / row["path"]).write_text(json.dumps(session, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        update_exec(exec_id, result_path=rel(dest))
        if data["status"] == "blocked":
            transition_exec(exec_id, "BLOCKED", action="result-ingest", reason="agent reported blocked")
        elif data["status"] == "failed":
            transition_exec(exec_id, "FAILED", action="result-ingest", reason="agent reported failed")
        else:
            transition_exec(exec_id, "RESULT_INGESTED", action="result-ingest", reason="structured agent result ingested")
        append_event("EXECUTION_RESULT_INGESTED", target=exec_id, action="ingest", reason="structured agent result stored and compared with actual diff", metadata=comparison)
        return {"execution_id": exec_id, "agent_status": data["status"], **comparison}


def check_execution(exec_id: str, *, advance: bool = True) -> dict:
    with target_lock(exec_id, "check"):
        row = find_exec(exec_id)
        freshness = verify_contract(exec_id)
        actual = changed_files(row)
        scope = scope_check(row["target"], actual)
        result_claim = load_json(ROOT / row["result_path"]) if row.get("result_path") and (ROOT / row["result_path"]).exists() else {}
        agent_result = result_claim.get("agent_result", {}) if result_claim else {}
        declared = sorted(set(str(x) for x in agent_result.get("changed_files", [])))
        diff_match = set(actual) == set(declared) if agent_result else False
        env_now = environment_snapshot(Path(row["worktree"] or ROOT))
        session = load_json(ROOT / row["path"])
        env_before = session.get("environment", {})
        environment_drift = {
            "head_changed": env_before.get("head") != env_now.get("head"),
            "tool_changes": {k: {"before": env_before.get("tools", {}).get(k), "after": env_now.get("tools", {}).get(k)} for k in sorted(set(env_before.get("tools", {})) | set(env_now.get("tools", {}))) if env_before.get("tools", {}).get(k) != env_now.get("tools", {}).get(k)},
            "lockfiles_changed": env_before.get("lockfiles", []) != env_now.get("lockfiles", []),
        }
        checks = {
            "contract_valid": freshness["passed"], "scope_passed": scope["passed"],
            "result_ingested": bool(agent_result), "declared_diff_matches_actual": diff_match,
        }
        passed = all(checks.values())
        evidence = {
            "execution_id": exec_id, "target": row["target"], "checked": now_iso(),
            "passed": passed, "checks": checks, "contract": freshness, "scope": scope,
            "actual_changed_files": actual, "declared_changed_files": declared,
            "environment_drift": environment_drift,
        }
        path = EVIDENCE / f"{exec_id}-execution-check.json"
        EVIDENCE.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if passed and advance and row["status"] == "RESULT_INGESTED":
            transition_exec(exec_id, "VERIFIED", action="execution-check", reason="contract, scope, result, and diff invariants passed")
        append_event("EXECUTION_CHECKED", target=exec_id, action="check", reason="EOSE execution invariants evaluated", metadata={"passed": passed, "evidence": rel(path)})
        return evidence


def print_json_or_text(value: dict, *, as_json: bool, title: str = "") -> None:
    if as_json:
        print(json.dumps(value, indent=2, sort_keys=True))
        return
    if title: print(title); print()
    for key, val in value.items():
        if isinstance(val, (dict, list)):
            print(f"{key}: {json.dumps(val, indent=2, sort_keys=True)}")
        else:
            print(f"{key}: {val}")


def cmd_preflight(args: argparse.Namespace) -> None:
    report = preflight(args.target, no_worktree=args.no_worktree, base=args.base)
    print(json.dumps(report, indent=2, sort_keys=True) if args.json else format_preflight(report))
    if not report["passed"]:
        raise EoseError("preflight failed")


def cmd_execute(args: argparse.Namespace) -> None:
    row, payload = create_session(args.target, no_worktree=args.no_worktree, base=args.base, actor=args.actor)
    output = {"execution_id": row["id"], "target": row["target"], "status": row["status"], "branch": row["branch"], "worktree": row["worktree"], "baseline_commit": row["baseline_commit"], "governing_hash": row["governing_hash"], "contract_hash": row["contract_hash"], "contract_markdown": f".eos/contracts/{row['id']}-{row['target']}.codex.md", "contract_json": f".eos/contracts/{row['id']}-{row['target']}.codex.json"}
    print_json_or_text(output, as_json=args.json, title="EOSE EXECUTION SESSION CREATED")


def cmd_codex(args: argparse.Namespace) -> None:
    if args.force:
        raise EoseError("--force cannot bypass EOSE v2 authorization/preflight. Use the governed authorization override mechanism before execution.")
    active = active_exec_for(args.target)
    if active:
        row = active[-1]
        session = load_json(ROOT / row["path"])
        contract = ROOT / session["contract"]["markdown"]
    else:
        row, _ = create_session(args.target, no_worktree=args.no_worktree, base=args.base, actor=args.actor)
        contract = CONTRACTS / f"{row['id']}-{row['target']}.codex.md"
    if args.json:
        session = load_json(ROOT / row["path"])
        print((ROOT / session["contract"]["json"]).read_text(encoding="utf-8"), end="")
    else:
        print(contract.read_text(encoding="utf-8"), end="")
        print(f"\nContract: {rel(contract)}", file=sys.stderr)


def cmd_worktree(args: argparse.Namespace) -> None:
    if args.worktree_command == "list":
        print(json.dumps(git_worktrees(), indent=2, sort_keys=True) if args.json else "\n".join(f"{w.get('worktree','')}\t{w.get('branch','')}" for w in git_worktrees()))
        return
    if args.worktree_command == "create":
        report = preflight(args.target, no_worktree=False, base=args.base)
        if not report["passed"] and not args.force:
            raise EoseError("worktree preflight failed:\n" + format_preflight(report))
        branch, path = create_worktree(args.target, base=args.base, custom_path=args.path)
        print(f"branch: {branch}\nworktree: {path}")
        return
    if args.worktree_command == "remove":
        remove_worktree(args.target, force=args.force)
        print(f"Removed worktree for {args.target}.")
        return


def cmd_execution(args: argparse.Namespace) -> None:
    sub = args.execution_command
    if sub == "list":
        selected = [r for r in rows() if not args.target or r.get("target") == args.target]
        if args.json: print(json.dumps(selected, indent=2, sort_keys=True)); return
        for r in selected: print(f"{r['id']}\t{r['target']}\t{r['status']}\t{r['branch']}\t{r['worktree']}")
        return
    if sub == "show":
        r = find_exec(args.execution_id); session = load_json(ROOT / r["path"])
        print(json.dumps({"registry": r, "session": session}, indent=2, sort_keys=True) if args.json else json.dumps({"registry": r, "session": session}, indent=2, sort_keys=True))
        return
    if sub == "ingest":
        result = ingest_result(args.execution_id, Path(args.result).expanduser().resolve())
        print(json.dumps(result, indent=2, sort_keys=True) if args.json else f"Ingested result for {args.execution_id}. scope={'PASS' if result['scope']['passed'] else 'FAIL'}")
        if result.get("agent_status") == "completed" and not result["scope"]["passed"]:
            raise EoseError("execution result ingested, but actual changes violate scope")
        return
    if sub == "check":
        result = check_execution(args.execution_id)
        print(json.dumps(result, indent=2, sort_keys=True) if args.json else f"{args.execution_id}: {'PASS' if result['passed'] else 'FAIL'}\nEvidence: .eos/evidence/{args.execution_id}-execution-check.json")
        if not result["passed"]: raise EoseError("execution checks failed")
        return
    if sub == "close":
        with target_lock(args.execution_id, "close"):
            r = find_exec(args.execution_id)
            if r["status"] != "VERIFIED": raise EoseError(f"{args.execution_id} must be VERIFIED before close; current={r['status']}")
            transition_exec(args.execution_id, "CLOSED", action="close", reason=args.reason or "execution session closed", actor=args.by)
            print(f"{args.execution_id} CLOSED.")
        return
    if sub == "abort":
        with target_lock(args.execution_id, "abort"):
            r = find_exec(args.execution_id)
            if r["status"] in TERMINAL_EXEC_STATES: raise EoseError(f"{args.execution_id} is already terminal: {r['status']}")
            if not args.reason.strip(): raise EoseError("abort requires --reason")
            transition_exec(args.execution_id, "ABORTED", action="abort", reason=args.reason, actor=args.by)
            print(f"{args.execution_id} ABORTED.")
        return
    if sub == "environment":
        r = find_exec(args.execution_id)
        print(json.dumps(environment_snapshot(Path(r["worktree"] or ROOT)), indent=2, sort_keys=True))
        return


def cmd_contract(args: argparse.Namespace) -> None:
    if args.contract_command == "verify":
        result = verify_contract(args.execution_id)
        print(json.dumps(result, indent=2, sort_keys=True) if args.json else "\n".join(f"{'PASS' if c['passed'] else 'FAIL'} {c['check']}: {c['detail']}" for c in result["checks"]))
        if not result["passed"]: raise EoseError("contract verification failed")
        return
    if args.contract_command == "show":
        r, contract = contract_for_exec(args.execution_id)
        if args.json: print(json.dumps(contract, indent=2, sort_keys=True))
        else:
            session = load_json(ROOT / r["path"])
            print((ROOT / session["contract"]["markdown"]).read_text(encoding="utf-8"), end="")
        return


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="./scripts/eos", description="EOSE Execution v2")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("preflight", help="Check whether a WP is safe to execute")
    p.add_argument("target"); p.add_argument("--no-worktree", action="store_true"); p.add_argument("--base", default="HEAD"); p.add_argument("--json", action="store_true"); p.set_defaults(func=cmd_preflight)

    p = sub.add_parser("execute", help="Create isolated execution session, worktree, branch, and contracts")
    p.add_argument("target"); p.add_argument("--no-worktree", action="store_true"); p.add_argument("--base", default="HEAD"); p.add_argument("--actor", default=""); p.add_argument("--json", action="store_true"); p.set_defaults(func=cmd_execute)

    p = sub.add_parser("codex", help="Create/reuse an EOSE v2 execution session and render its Codex contract")
    p.add_argument("target"); p.add_argument("--force", action="store_true", help=argparse.SUPPRESS); p.add_argument("--no-worktree", action="store_true"); p.add_argument("--base", default="HEAD"); p.add_argument("--actor", default="codex"); p.add_argument("--json", action="store_true"); p.set_defaults(func=cmd_codex)

    w = sub.add_parser("worktree", help="Manage governed execution worktrees"); ws = w.add_subparsers(dest="worktree_command", required=True)
    p = ws.add_parser("create"); p.add_argument("target"); p.add_argument("--base", default="HEAD"); p.add_argument("--path", default=""); p.add_argument("--force", action="store_true"); p.set_defaults(func=cmd_worktree)
    p = ws.add_parser("list"); p.add_argument("--json", action="store_true"); p.set_defaults(func=cmd_worktree)
    p = ws.add_parser("remove"); p.add_argument("target"); p.add_argument("--force", action="store_true"); p.set_defaults(func=cmd_worktree)

    e = sub.add_parser("execution", help="Inspect and govern EXEC-* sessions"); es = e.add_subparsers(dest="execution_command", required=True)
    p = es.add_parser("list"); p.add_argument("--target", default=""); p.add_argument("--json", action="store_true"); p.set_defaults(func=cmd_execution)
    p = es.add_parser("show"); p.add_argument("execution_id"); p.add_argument("--json", action="store_true"); p.set_defaults(func=cmd_execution)
    p = es.add_parser("ingest"); p.add_argument("execution_id"); p.add_argument("result"); p.add_argument("--json", action="store_true"); p.set_defaults(func=cmd_execution)
    p = es.add_parser("check"); p.add_argument("execution_id"); p.add_argument("--json", action="store_true"); p.set_defaults(func=cmd_execution)
    p = es.add_parser("close"); p.add_argument("execution_id"); p.add_argument("--reason", default=""); p.add_argument("--by", default=""); p.set_defaults(func=cmd_execution)
    p = es.add_parser("abort"); p.add_argument("execution_id"); p.add_argument("--reason", required=True); p.add_argument("--by", default=""); p.set_defaults(func=cmd_execution)
    p = es.add_parser("environment"); p.add_argument("execution_id"); p.set_defaults(func=cmd_execution)

    c = sub.add_parser("contract", help="Show/verify fingerprinted execution contracts"); cs = c.add_subparsers(dest="contract_command", required=True)
    p = cs.add_parser("verify"); p.add_argument("execution_id"); p.add_argument("--json", action="store_true"); p.set_defaults(func=cmd_contract)
    p = cs.add_parser("show"); p.add_argument("execution_id"); p.add_argument("--json", action="store_true"); p.set_defaults(func=cmd_contract)
    return parser


def main() -> int:
    for d in (EXEC_DIR, CONTRACTS, EVIDENCE, LOCKS): d.mkdir(parents=True, exist_ok=True)
    parser = build_parser(); args = parser.parse_args()
    try:
        args.func(args); return 0
    except EoseError as exc:
        print(f"ERROR: {exc}", file=sys.stderr); return 2
    except subprocess.CalledProcessError as exc:
        print(f"ERROR: command failed ({exc.returncode}): {' '.join(exc.cmd)}", file=sys.stderr)
        if exc.stdout: print(exc.stdout, file=sys.stderr)
        if exc.stderr: print(exc.stderr, file=sys.stderr)
        return exc.returncode or 1


if __name__ == "__main__":
    raise SystemExit(main())
