#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import datetime as dt
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
from pathlib import Path
from typing import Iterable

UTC = dt.timezone.utc
EVID_FIELDS = [
    "id", "path", "target", "execution", "validator", "profile", "kind",
    "status", "result", "exit_code", "command", "source_hash",
    "environment_hash", "artifact_hash", "covers", "created", "updated",
]
LINK_FIELDS = ["evidence_id", "reference", "relation", "created", "actor"]
PERF_FIELDS = ["id", "name", "target", "unit", "direction", "baseline", "tolerance", "created", "updated"]
ID_RE = re.compile(r"\b(?:REQ-[A-Z0-9][A-Z0-9-]*|SPEC-[A-Z0-9][A-Z0-9-]*|ADR-\d{4}|QA-[A-Z0-9][A-Z0-9-]*|CAP-[A-Z0-9][A-Z0-9-]*|PI(?:-[A-Z][A-Z0-9]*)?-\d{3}|WC(?:-[A-Z][A-Z0-9]*)?-\d{4}|WP(?:-[A-Z][A-Z0-9]*)?-\d{4}|EXEC-\d{4}|EVID-\d{4})\b")
AC_RE = re.compile(r"^\s*-\s*\[[ xX]\]\s*(AC-[A-Z0-9][A-Z0-9-]*)\s*(?::|—|-)\s*(.+)$")
SECRET_PATTERNS = {
    "private-key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    "aws-access-key": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "github-token": re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,255}\b"),
    "github-fine-grained-token": re.compile(r"\bgithub_pat_[A-Za-z0-9_]{50,255}\b"),
}
MANIFEST_NAMES = {
    "package.json", "bun.lock", "bun.lockb", "package-lock.json", "pnpm-lock.yaml", "yarn.lock",
    "Cargo.toml", "Cargo.lock", "go.mod", "go.sum", "pyproject.toml", "poetry.lock",
    "requirements.txt", "Pipfile.lock", "Gemfile.lock", "composer.lock", "pom.xml",
    "gradle.lockfile", "build.gradle", "build.gradle.kts",
}

class EosvError(RuntimeError):
    pass

def now_iso() -> str:
    return dt.datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def discover_root() -> Path:
    explicit = os.environ.get("EOS_ROOT", "").strip()
    if explicit:
        return Path(explicit).resolve()
    candidate = Path(__file__).resolve().parents[2]
    if (candidate / ".eos").exists():
        return candidate
    try:
        p = subprocess.run(["git", "rev-parse", "--show-toplevel"], text=True, capture_output=True, check=True)
        return Path(p.stdout.strip()).resolve()
    except Exception:
        return candidate

ROOT = discover_root()
EOS = ROOT / ".eos"
CORE = ROOT / "tools" / "eos" / "eos.py"
EVID_REG = EOS / "evidence.tsv"
LINK_REG = EOS / "evidence-links.tsv"
PERF_REG = EOS / "performance-baselines.tsv"
EVENTS = EOS / "events.jsonl"


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def run(args: list[str], *, cwd: Path | None = None, check: bool = False, shell: bool = False) -> subprocess.CompletedProcess[str]:
    if shell:
        return subprocess.run(["bash", "-lc", args[0]], cwd=cwd or ROOT, text=True, capture_output=True, check=check)
    return subprocess.run(args, cwd=cwd or ROOT, text=True, capture_output=True, check=check)


def core(*args: str) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ); env["EOS_ROOT"] = str(ROOT)
    return subprocess.run([sys.executable, str(CORE), *args], cwd=ROOT, env=env, text=True, capture_output=True)


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists(): return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def write_tsv(path: Path, fields: list[str], rows: Iterable[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter="\t", lineterminator="\n")
        w.writeheader()
        for row in rows: w.writerow({k: row.get(k, "") for k in fields})
        f.flush(); os.fsync(f.fileno())
    tmp.replace(path)


def load_json(path: Path, default=None):
    if not path.exists():
        if default is not None: return default
        raise EosvError(f"Missing {rel(path)}")
    try: return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc: raise EosvError(f"Invalid JSON in {rel(path)}: {exc}") from exc


def sha256_bytes(data: bytes) -> str: return hashlib.sha256(data).hexdigest()
def canonical_hash(obj) -> str: return sha256_bytes(json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode())
def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""): h.update(chunk)
    return h.hexdigest()


def append_event(event_type: str, target: str, *, from_state="", to_state="", action="", reason="", metadata=None, entity_kind="EVID") -> None:
    evt = {
        "event_id": "EVT-" + uuid.uuid4().hex.upper(), "schema_version": "1.0.0",
        "timestamp": now_iso(), "event_type": event_type,
        "actor": os.environ.get("EOS_ACTOR") or os.environ.get("USER") or "unknown",
        "target": target, "entity_kind": entity_kind, "action": action,
        "from_state": from_state, "to_state": to_state, "reason": reason,
        "commit": git_head(ROOT), "metadata": metadata or {},
    }
    with EVENTS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(evt, sort_keys=True, separators=(",", ":")) + "\n"); f.flush(); os.fsync(f.fileno())


def git_head(cwd: Path) -> str:
    p=run(["git","rev-parse","HEAD"],cwd=cwd); return p.stdout.strip() if p.returncode==0 else ""

def git_root(cwd: Path) -> Path:
    p=run(["git","rev-parse","--show-toplevel"],cwd=cwd); return Path(p.stdout.strip()).resolve() if p.returncode==0 else cwd

def semantic_file_hash(path: Path) -> str:
    if path.suffix.lower() != ".md":
        return file_hash(path)

    text = path.read_text(encoding="utf-8", errors="strict")
    lines = text.splitlines()
    out = []

    in_fm = bool(lines and lines[0].strip() == "---")
    closed = not in_fm

    for i, line in enumerate(lines):
        if in_fm and i == 0:
            out.append(line)
            continue

        if in_fm and not closed:
            if line.strip() == "---":
                closed = True
                out.append(line)
                continue

            if re.match(r"^(status|updated):\s*", line):
                continue

            out.append(line)
            continue

        if re.match(r"^\*\*(?:State|Status):\*\*\s*", line):
            continue

        out.append(line)

    return sha256_bytes(
        ("\n".join(out).rstrip() + "\n").encode()
    )

def artifact_path(target: str) -> Path | None:
    tables=("program-increments.tsv","work-cycles.tsv","work-packets.tsv","change-requests.tsv","maintenance.tsv","releases.tsv","executions.tsv","evidence.tsv")
    for table in tables:
        for row in read_tsv(EOS/table):
            if row.get("id")==target and row.get("path"):
                p=ROOT/row["path"]
                if p.exists(): return p
    for row in read_tsv(EOS/"artifacts.tsv"):
        if row.get("artifact_id")==target and row.get("path"):
            p=ROOT/row["path"]
            if p.exists(): return p
    return None


def wp_row(target: str) -> dict[str,str] | None:
    for row in read_tsv(EOS/"work-packets.tsv"):
        if row.get("id")==target: return row
    return None


def exec_row(target: str) -> dict[str,str] | None:
    for row in read_tsv(EOS/"executions.tsv"):
        if row.get("id")==target: return row
    return None


def context_for_target(target: str, execution: str="") -> tuple[str,str,Path,str]:
    exec_id=execution
    wp=target
    if target.startswith("EXEC-"):
        er=exec_row(target)
        if not er: raise EosvError(f"Unknown execution: {target}")
        exec_id=target; wp=er.get("target","")
    er=exec_row(exec_id) if exec_id else None
    cwd=Path(er["worktree"]).resolve() if er and er.get("worktree") and Path(er["worktree"]).exists() else ROOT
    baseline=er.get("baseline_commit","") if er else git_head(cwd)
    return wp, exec_id, cwd, baseline


def references_from(path: Path) -> list[str]:
    if not path.exists(): return []
    text=path.read_text(encoding="utf-8",errors="ignore")
    return sorted(set(ID_RE.findall(text)))


def workspace_hash(cwd: Path, baseline: str) -> str:
    """Hash execution-relevant current source independently of Git history depth.

    The immutable execution baseline remains separately bound in source_fingerprint().
    Generated EOS/evidence/machine outputs are excluded by source_content_hash().
    """
    _ = baseline
    return source_content_hash(cwd)


SOURCE_EXCLUDED_PATHS = (
    ".eos/",
    "machine/",
    "engineering/evidence/",
    "engineering/reviews/",
)
SOURCE_EXCLUDED_PARTS = {
    ".git", ".hg", ".svn", "__pycache__", ".pytest_cache", ".mypy_cache",
    ".ruff_cache", ".tox", ".venv", "venv", "node_modules", "target", "build",
    "dist", "vendor",
}


def is_source_path(path: Path, cwd: Path) -> bool:
    try:
        relative = path.relative_to(cwd).as_posix()
    except ValueError:
        return False
    return not (
        relative.startswith(SOURCE_EXCLUDED_PATHS)
        or any(part in SOURCE_EXCLUDED_PARTS for part in Path(relative).parts)
    )


def source_content_hash(cwd: Path) -> str:
    """Hash relevant tracked and untracked content for non-execution evidence."""
    paths: set[Path] = set()
    if (cwd / ".git").exists() or run(["git", "rev-parse", "--git-dir"], cwd=cwd).returncode == 0:
        listed = run(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=cwd)
        for item in listed.stdout.splitlines():
            candidate = cwd / item
            if item and candidate.is_file() and is_source_path(candidate, cwd): paths.add(candidate)
    else:
        for candidate in cwd.rglob("*"):
            if candidate.is_file() and is_source_path(candidate, cwd): paths.add(candidate)
    pieces = [
        f"{path.relative_to(cwd).as_posix()}:{semantic_file_hash(path)}"
        for path in sorted(paths, key=lambda p: p.relative_to(cwd).as_posix())
    ]
    return sha256_bytes("\n".join(pieces).encode())


def source_fingerprint(target: str, execution: str="") -> tuple[str, dict]:
    wp, exec_id, cwd, baseline=context_for_target(target,execution)
    paths=[]; ids=[]
    wp_path=artifact_path(wp) if wp else artifact_path(target)
    if wp_path and wp_path.exists():
        paths.append(wp_path); ids.extend(references_from(wp_path))
    row=wp_row(wp) if wp else None
    if row:
        ids.extend([row.get("pi",""),row.get("wc","")])
    for rid in sorted(set(i for i in ids if i and i not in {target,exec_id,wp})):
        p=artifact_path(rid)
        if p and p.exists(): paths.append(p)
    semantic={rel(p):semantic_file_hash(p) for p in sorted(set(paths),key=lambda p:rel(p))}
    payload={"target":target,"work_packet":wp,"execution":exec_id,"governing":semantic}
    if exec_id:
        # Execution evidence remains bound to its immutable EOSE baseline.
        payload.update({"workspace_hash":workspace_hash(cwd,baseline),"baseline":baseline})
    else:
        payload["source_content_hash"] = source_content_hash(cwd)
    return canonical_hash(payload), payload


def environment_snapshot(cwd: Path) -> dict:
    def version(cmd):
        exe=shutil.which(cmd[0]);
        if not exe: return ""
        p=run(cmd,cwd=cwd); return (p.stdout+p.stderr).strip().splitlines()[0][:300] if (p.stdout+p.stderr).strip() else ""
    lockfiles={}
    for name in ("bun.lock","bun.lockb","package-lock.json","pnpm-lock.yaml","yarn.lock","Cargo.lock","go.sum","poetry.lock","Pipfile.lock","Gemfile.lock","composer.lock"):
        for p in cwd.rglob(name):
            if any(part in {".git",".eos","node_modules","target","vendor","dist"} for part in p.parts): continue
            try: lockfiles[p.relative_to(cwd).as_posix()]=file_hash(p)
            except OSError: pass
    return {
        "platform":platform.platform(),"machine":platform.machine(),"hostname":socket.gethostname(),
        "python":sys.version.split()[0],"git":version(["git","--version"]),"bash":version(["bash","--version"]),
        "node":version(["node","--version"]),"bun":version(["bun","--version"]),"go":version(["go","version"]),
        "rustc":version(["rustc","--version"]),"cargo":version(["cargo","--version"]),"lockfiles":lockfiles,
    }


def merged_validators() -> dict:
    base=load_json(EOS/"validators.json",{}).get("validators",{})
    local=load_json(EOS/"validators.local.json",{"validators":{}}).get("validators",{})
    if not isinstance(base,dict) or not isinstance(local,dict): raise EosvError("validator definitions must be objects")
    merged=dict(base); merged.update(local); return merged


def profiles() -> dict:
    p=load_json(EOS/"validation-profiles.json",{}).get("profiles",{})
    if not isinstance(p,dict): raise EosvError("validation profiles must be an object")
    return p


def normalize_output(text: str) -> str:
    lines=[]
    for line in text.replace("\r\n","\n").splitlines():
        # Normalize common volatile timestamps while preserving substantive output.
        line=re.sub(r"\b\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z\b","<TIMESTAMP>",line)
        lines.append(line.rstrip())
    return "\n".join(lines).strip()


def tracked_candidate_files(cwd: Path) -> list[Path]:
    p=run(["git","ls-files","-co","--exclude-standard","-z"],cwd=cwd)
    if p.returncode!=0: return []
    out=[]
    for raw in p.stdout.split("\0"):
        if not raw: continue
        fp=cwd/raw
        if not fp.is_file(): continue
        r=fp.relative_to(cwd).as_posix()
        if r.startswith(".eos/") or "/node_modules/" in f"/{r}/" or "/.git/" in f"/{r}/": continue
        out.append(fp)
    return out


def builtin_secret_scan(cwd: Path) -> dict:
    findings=[]
    for fp in tracked_candidate_files(cwd):
        try:
            if fp.stat().st_size>2_000_000: continue
            text=fp.read_text(encoding="utf-8",errors="ignore")
        except OSError: continue
        for name,pat in SECRET_PATTERNS.items():
            if pat.search(text): findings.append({"path":fp.relative_to(cwd).as_posix(),"pattern":name})
    return {"result":"FAILED" if findings else "PASSED","exit_code":1 if findings else 0,"output":json.dumps(findings,indent=2),"details":{"findings":findings},"command":"builtin:secret-scan"}


def builtin_supply_chain(cwd: Path) -> dict:
    inventory=[]
    for fp in tracked_candidate_files(cwd):
        if fp.name in MANIFEST_NAMES:
            inventory.append({"path":fp.relative_to(cwd).as_posix(),"sha256":file_hash(fp)})
    inventory=sorted(inventory,key=lambda x:x["path"])
    return {"result":"PASSED","exit_code":0,"output":json.dumps(inventory,indent=2),"details":{"manifests":inventory,"count":len(inventory)},"command":"builtin:supply-chain"}


def builtin_execution_acceptance(exec_id: str) -> dict:
    if not exec_id: return {"result":"SKIPPED","exit_code":0,"output":"No EXEC session selected.","details":{},"command":"builtin:execution-acceptance","covers":[]}
    er=exec_row(exec_id)
    if not er or not er.get("result_path"): return {"result":"SKIPPED","exit_code":0,"output":"Execution result has not been ingested.","details":{},"command":"builtin:execution-acceptance","covers":[]}
    path=Path(er["result_path"]); path=path if path.is_absolute() else ROOT/path
    if not path.exists(): return {"result":"FAILED","exit_code":2,"output":f"Missing execution result: {path}","details":{},"command":"builtin:execution-acceptance","covers":[]}
    data=load_json(path,{})
    if isinstance(data, dict) and isinstance(data.get("agent_result"), dict):
        data = data["agent_result"]
    items=data.get("acceptance_criteria",[]) if isinstance(data,dict) else []
    failed=[]; covers=[]
    for item in items if isinstance(items,list) else []:
        if not isinstance(item,dict): continue
        label=str(item.get("criterion","")); covers.extend(re.findall(r"\bAC-[A-Z0-9][A-Z0-9-]*\b",label))
        if str(item.get("status","")).lower() not in {"passed","pass","satisfied","complete","completed"}: failed.append(item)
    if not items: return {"result":"SKIPPED","exit_code":0,"output":"No structured acceptance_criteria in execution result.","details":{},"command":"builtin:execution-acceptance","covers":[]}
    return {"result":"FAILED" if failed else "PASSED","exit_code":1 if failed else 0,"output":json.dumps(items,indent=2),"details":{"criteria":items,"failed":failed},"command":"builtin:execution-acceptance","covers":sorted(set(covers))}


def run_legacy_commands(cwd: Path) -> dict:
    cfg=EOS/"validation.commands"; commands=[]
    if cfg.exists(): commands=[x.strip() for x in cfg.read_text().splitlines() if x.strip() and not x.lstrip().startswith("#")]
    if not commands: return {"result":"SKIPPED","exit_code":0,"output":"No repository validation commands configured.","details":{},"command":"legacy:.eos/validation.commands"}
    results=[]; failed=False
    for cmd in commands:
        p=run([cmd],cwd=cwd,shell=True); failed|=p.returncode!=0
        results.append({"command":cmd,"exit_code":p.returncode,"output":(p.stdout+p.stderr)[-20000:]})
    return {"result":"FAILED" if failed else "PASSED","exit_code":1 if failed else 0,"output":json.dumps(results,indent=2),"details":{"commands":results},"command":"legacy:.eos/validation.commands"}


def builtin_reproducibility(cwd: Path) -> dict:
    cfg=EOS/"reproducibility.commands"; cmds=[]
    if cfg.exists(): cmds=[x.strip() for x in cfg.read_text().splitlines() if x.strip() and not x.lstrip().startswith("#")]
    if not cmds: return {"result":"SKIPPED","exit_code":0,"output":"No reproducibility commands configured.","details":{},"command":"builtin:reproducibility"}
    results=[]; failed=False
    for cmd in cmds:
        runs=[]
        for _ in range(2):
            p=run([cmd],cwd=cwd,shell=True); norm=normalize_output(p.stdout+p.stderr); runs.append({"exit_code":p.returncode,"hash":sha256_bytes(norm.encode()),"output":norm[-10000:]})
        same=runs[0]["exit_code"]==runs[1]["exit_code"] and runs[0]["hash"]==runs[1]["hash"]; failed|=not same
        results.append({"command":cmd,"reproducible":same,"runs":runs})
    return {"result":"FAILED" if failed else "PASSED","exit_code":1 if failed else 0,"output":json.dumps(results,indent=2),"details":{"commands":results},"command":"builtin:reproducibility"}


def performance_rows() -> list[dict[str,str]]: return read_tsv(PERF_REG)

def find_perf(name: str, target: str="") -> dict[str,str] | None:
    candidates=[r for r in performance_rows() if r.get("name")==name and (not target or r.get("target") in {"",target})]
    if not candidates: return None
    candidates.sort(key=lambda r:(r.get("target")!=target,r.get("updated",""))); return candidates[0]


def performance_pass(row: dict[str,str], value: float) -> tuple[bool,float]:
    baseline=float(row["baseline"]); tolerance=float(row.get("tolerance") or 0)
    direction=row.get("direction","lower")
    if direction=="lower": limit=baseline*(1+tolerance); return value<=limit,limit
    if direction=="higher": limit=baseline*(1-tolerance); return value>=limit,limit
    limit=baseline*tolerance; return abs(value-baseline)<=limit,limit


def builtin_performance(cwd: Path, target: str) -> dict:
    cfg=EOS/"performance.commands"; entries=[]
    if cfg.exists():
        for raw in cfg.read_text().splitlines():
            if not raw.strip() or raw.lstrip().startswith("#"): continue
            parts=raw.split("\t",2)
            if len(parts)!=3: return {"result":"FAILED","exit_code":2,"output":f"Malformed performance.commands line: {raw}","details":{},"command":"builtin:performance"}
            entries.append(parts)
    if not entries: return {"result":"SKIPPED","exit_code":0,"output":"No performance commands configured.","details":{},"command":"builtin:performance"}
    results=[]; failed=False
    for name,unit,cmd in entries:
        p=run([cmd],cwd=cwd,shell=True); text=p.stdout.strip()
        try: value=float(text)
        except ValueError: results.append({"name":name,"command":cmd,"error":f"expected numeric stdout, got {text!r}"}); failed=True; continue
        base=find_perf(name,target)
        if not base: results.append({"name":name,"value":value,"unit":unit,"status":"NO_BASELINE"}); failed=True; continue
        ok,limit=performance_pass(base,value); failed|=not ok
        results.append({"name":name,"value":value,"unit":unit,"baseline":float(base["baseline"]),"direction":base["direction"],"tolerance":float(base["tolerance"]),"limit":limit,"passed":ok})
    return {"result":"FAILED" if failed else "PASSED","exit_code":1 if failed else 0,"output":json.dumps(results,indent=2),"details":{"benchmarks":results},"command":"builtin:performance"}


def run_validator(vid: str, definition: dict, *, cwd: Path, target: str, exec_id: str) -> dict:
    runner=definition.get("runner")
    if runner=="legacy-lines": return run_legacy_commands(cwd)
    if runner=="command":
        cmd=str(definition.get("command","")).strip()
        if not cmd: return {"result":"SKIPPED","exit_code":0,"output":"No command configured.","details":{},"command":""}
        p=run([cmd],cwd=cwd,shell=True); return {"result":"PASSED" if p.returncode==0 else "FAILED","exit_code":p.returncode,"output":p.stdout+p.stderr,"details":{},"command":cmd,"covers":definition.get("covers",[])}
    builtin=definition.get("builtin")
    if builtin=="core-verify":
        p=core("verify","--strict"); return {"result":"PASSED" if p.returncode==0 else "FAILED","exit_code":p.returncode,"output":p.stdout+p.stderr,"details":{},"command":"eos-core:verify --strict"}
    if builtin=="execution-acceptance": return builtin_execution_acceptance(exec_id)
    if builtin=="secret-scan": return builtin_secret_scan(cwd)
    if builtin=="supply-chain": return builtin_supply_chain(cwd)
    if builtin=="reproducibility": return builtin_reproducibility(cwd)
    if builtin=="performance": return builtin_performance(cwd,target)
    raise EosvError(f"Unknown validator runner for {vid}: {definition}")


def next_id(prefix: str, rows: list[dict[str,str]]) -> str:
    nums=[]
    for r in rows:
        m=re.fullmatch(re.escape(prefix)+r"-(\d{4})",r.get("id",""))
        if m: nums.append(int(m.group(1)))
    return f"{prefix}-{max(nums,default=0)+1:04d}"


def append_artifact_registry(evid: str, path: str) -> None:
    reg=EOS/"artifacts.tsv"; rows=read_tsv(reg)
    if any(r.get("artifact_id")==evid for r in rows): return
    fields=["artifact_id","path","type","authority"]
    rows.append({"artifact_id":evid,"path":path,"type":"verification-evidence","authority":"evidence-authoritative"})
    write_tsv(reg,fields,rows)


def sync_human_evidence_state(path_text: str, state: str) -> None:
    path=ROOT/path_text
    if not path.exists(): return
    text=path.read_text(encoding="utf-8")
    text=re.sub(r'^status:\s*"[^"]*"', f'status: "{state}"', text, count=1, flags=re.M)
    text=re.sub(r'^updated:\s*"[^"]*"', f'updated: "{now_iso()[:10]}"', text, count=1, flags=re.M)
    path.write_text(text,encoding="utf-8")


def transition_evidence(evid: str, to_state: str, reason: str) -> None:
    rows=read_tsv(EVID_REG)
    for row in rows:
        if row.get("id")==evid:
            old=row.get("status",""); row["status"]=to_state; row["updated"]=now_iso(); write_tsv(EVID_REG,EVID_FIELDS,rows)
            sync_human_evidence_state(row.get("path",""),to_state)
            append_event("STATE_TRANSITION",evid,from_state=old,to_state=to_state,action="evidence",reason=reason)
            return
    raise EosvError(f"Unknown evidence: {evid}")


def supersede_previous(target: str, validator: str, new_id: str) -> None:
    rows=read_tsv(EVID_REG); changed=False
    for row in rows:
        if row.get("id")!=new_id and row.get("target")==target and row.get("validator")==validator and row.get("status") in {"VALIDATED","STALE","FAILED"}:
            old=row["status"]; row["status"]="SUPERSEDED"; row["updated"]=now_iso(); changed=True
            sync_human_evidence_state(row.get("path",""),"SUPERSEDED")
            append_event("STATE_TRANSITION",row["id"],from_state=old,to_state="SUPERSEDED",action="supersede",reason=f"superseded by {new_id}")
    if changed: write_tsv(EVID_REG,EVID_FIELDS,rows)


def create_evidence(*, target: str, exec_id: str, profile: str, vid: str, kind: str, result: dict, source_hash: str, env_hash: str, env: dict, covers: list[str]) -> dict[str,str]:
    rows=read_tsv(EVID_REG); evid=next_id("EVID",rows); created=now_iso()
    machine_path=EOS/"evidence"/f"{evid}.json"; human_path=ROOT/"engineering"/"evidence"/f"{evid}.md"; human_path.parent.mkdir(parents=True,exist_ok=True); machine_path.parent.mkdir(parents=True,exist_ok=True)
    payload={"id":evid,"target":target,"execution":exec_id,"profile":profile,"validator":vid,"kind":kind,"result":result.get("result"),"exit_code":result.get("exit_code"),"command":result.get("command", ""),"source_hash":source_hash,"environment_hash":env_hash,"environment":env,"covers":sorted(set(covers)),"output_hash":sha256_bytes(str(result.get("output","")).encode()),"output":str(result.get("output",""))[-50000:],"details":result.get("details",{}),"created":created,"producer":{"actor":os.environ.get("EOS_ACTOR") or os.environ.get("USER") or "unknown","commit":git_head(ROOT)}}
    machine_path.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8"); artifact_hash=file_hash(machine_path)
    final_state="FAILED" if result.get("result")=="FAILED" else "VALIDATED"
    body=f"""---\nartifact_id: "{evid}"\ntitle: "Verification Evidence {evid}"\ntype: "verification-evidence"\nversion: "1.0.0"\nstatus: "{final_state}"\nauthority: "evidence-authoritative"\ncreated: "{created[:10]}"\nupdated: "{created[:10]}"\n---\n\n# {evid} — Verification Evidence\n\n- Target: {target}\n- Execution: {exec_id or "(none)"}\n- Profile: {profile}\n- Validator: {vid}\n- Kind: {kind}\n- Result: {result.get("result")}\n- Exit code: {result.get("exit_code")}\n- Source fingerprint: `{source_hash}`\n- Environment fingerprint: `{env_hash}`\n- Machine evidence: `{rel(machine_path)}`\n- Machine evidence SHA-256: `{artifact_hash}`\n- Covers: {", ".join(sorted(set(covers))) or "(not explicitly mapped)"}\n\n## Command\n\n`{result.get("command","") or "(builtin)"}`\n\n## Output Digest\n\n`{payload["output_hash"]}`\n\nThe full bounded output and structured details are retained in the machine evidence artifact.\n"""
    human_path.write_text(body,encoding="utf-8")
    row={"id":evid,"path":rel(human_path),"target":target,"execution":exec_id,"validator":vid,"profile":profile,"kind":kind,"status":"CAPTURED","result":str(result.get("result", "")),"exit_code":str(result.get("exit_code", "")),"command":str(result.get("command", "")),"source_hash":source_hash,"environment_hash":env_hash,"artifact_hash":artifact_hash,"covers":",".join(sorted(set(covers))),"created":created,"updated":created}
    rows.append(row); write_tsv(EVID_REG,EVID_FIELDS,rows); append_artifact_registry(evid,rel(human_path))
    append_event("ENTITY_CREATED",evid,action="capture",metadata={"initial_state":"CAPTURED","target":target,"validator":vid,"path":rel(human_path)})
    transition_evidence(evid,final_state,"validator result captured and hashed")
    supersede_previous(target,vid,evid)
    return next(r for r in read_tsv(EVID_REG) if r.get("id")==evid)


def explicit_links(evid: str) -> list[str]: return [r.get("reference","") for r in read_tsv(LINK_REG) if r.get("evidence_id")==evid]

def evidence_covers(row: dict[str,str]) -> set[str]: return set(x for x in (row.get("covers","").split(",")+explicit_links(row.get("id",""))) if x)


def criteria_for_wp(wp: str) -> tuple[list[tuple[str,str]],int]:
    path=artifact_path(wp)
    if not path: return [],0
    criteria=[]; unidentified=0
    for line in path.read_text(encoding="utf-8",errors="ignore").splitlines():
        m=AC_RE.match(line)
        if m: criteria.append((m.group(1),m.group(2).strip()))
        elif re.match(r"^\s*-\s*\[[ xX]\]\s+",line): unidentified+=1
    return criteria,unidentified


def run_profile(target: str, profile: str, execution: str="", covers: list[str] | None=None, json_mode=False) -> dict:
    prof=profiles().get(profile)
    if not isinstance(prof,dict): raise EosvError(f"Unknown validation profile: {profile}")
    validators=merged_validators(); wp,exec_id,cwd,_=context_for_target(target,execution)
    canonical_target=wp or target
    if wp:
        row=wp_row(wp)
        if row and row.get("status")=="AUTHORIZED": raise EosvError(f"{wp} is AUTHORIZED; start execution before EOSV validation")
        if row and row.get("status")=="IN_PROGRESS":
            p=core("state-machine","WP")
            # Use core's existing validate transition semantics without running its validator body by projecting the legal transition directly through a tiny helper invocation.
            env=dict(os.environ); env["EOS_ROOT"]=str(ROOT)
            code='import importlib.util,os; from pathlib import Path; p=Path(os.environ["EOS_ROOT"])/"tools/eos/eos.py"; s=importlib.util.spec_from_file_location("eoscore",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); m.set_lifecycle_state("'+wp+'","VERIFYING",action="eosv-validate",actor=m.actor_name(),reason="EOSV Verification v2 started")'
            q=subprocess.run([sys.executable,"-c",code],cwd=ROOT,env=env,text=True,capture_output=True)
            if q.returncode!=0: raise EosvError(q.stderr or q.stdout)
    source_hash,source_detail=source_fingerprint(target,execution); env=environment_snapshot(cwd); env_hash=canonical_hash(env)
    required=list(prof.get("required",[])); optional=list(prof.get("optional",[])); results=[]; failed_required=[]
    for vid in required+optional:
        definition=validators.get(vid)
        if not isinstance(definition,dict):
            result={"result":"FAILED","exit_code":2,"output":f"Validator not defined: {vid}","details":{},"command":""}
            kind="configuration"
        else:
            kind=str(definition.get("kind","validation")); result=run_validator(vid,definition,cwd=cwd,target=canonical_target,exec_id=exec_id)
        inferred=list(covers or [])+list(result.get("covers",[]) or [])
        evid=create_evidence(target=canonical_target,exec_id=exec_id,profile=profile,vid=vid,kind=kind,result=result,source_hash=source_hash,env_hash=env_hash,env=env,covers=inferred)
        item={"validator":vid,"required":vid in required,"result":result.get("result"),"evidence":evid["id"]}; results.append(item)
        if vid in required and result.get("result")!="PASSED": failed_required.append(vid)
    report={"target":canonical_target,"execution":exec_id,"profile":profile,"source_hash":source_hash,"environment_hash":env_hash,"results":results,"passed":not failed_required,"failed_required":failed_required}
    if json_mode: print(json.dumps(report,indent=2,sort_keys=True))
    else:
        print(f"EOSV VALIDATION — {canonical_target}\nprofile: {profile}\nexecution: {exec_id or '(none)'}\n")
        for item in results: print(f"{'PASS' if item['result']=='PASSED' else 'SKIP' if item['result']=='SKIPPED' else 'FAIL':<5} {item['validator']:<24} {item['evidence']} {'required' if item['required'] else 'optional'}")
        print(f"\nRESULT: {'PASS' if report['passed'] else 'FAIL'}")
    if failed_required: raise EosvError("Required validators failed or were skipped: "+", ".join(failed_required))
    return report


def evidence_row(evid: str) -> dict[str,str]:
    for row in read_tsv(EVID_REG):
        if row.get("id")==evid: return row
    raise EosvError(f"Unknown evidence: {evid}")


def audit_evidence(*, mutate: bool=True) -> tuple[list[dict],list[str]]:
    report=[]; failures=[]
    for row in read_tsv(EVID_REG):
        evid=row.get("id",""); machine=EOS/"evidence"/f"{evid}.json"
        issues=[]
        if not machine.exists(): issues.append("machine evidence missing")
        elif row.get("artifact_hash")!=file_hash(machine): issues.append("machine evidence hash mismatch")
        if row.get("status") in {"VALIDATED","STALE"}:
            try: current,_=source_fingerprint(row.get("target", ""), row.get("execution", ""))
            except Exception as exc: current=""; issues.append(f"source fingerprint unavailable: {exc}")
            if current and current!=row.get("source_hash"):
                issues.append("source fingerprint changed")
                if mutate and row.get("status")=="VALIDATED": transition_evidence(evid,"STALE","governing or implementation source fingerprint changed")
        report.append({"id":evid,"status":row.get("status"),"issues":issues})
        if issues and "machine evidence hash mismatch" in issues: failures.append(f"{evid}: machine evidence hash mismatch")
    return report,failures


def verify_evidence(strict: bool) -> tuple[bool,str]:
    rows=read_tsv(EVID_REG); ids=set(); failures=[]; warnings=[]
    for row in rows:
        if row.get("id") in ids: failures.append(f"duplicate evidence id: {row.get('id')}")
        ids.add(row.get("id"))
        if row.get("status") not in {"CAPTURED","VALIDATED","FAILED","STALE","SUPERSEDED"}: failures.append(f"{row.get('id')}: invalid status {row.get('status')}")
    audit,hard=audit_evidence(mutate=True); failures.extend(hard)
    latest={}
    for row in read_tsv(EVID_REG):
        if row.get("status")=="SUPERSEDED": continue
        latest[(row.get("target"),row.get("validator"))]=row
    stale=[r for r in latest.values() if r.get("status")=="STALE"]
    if stale:
        msgs=[f"{r['id']} target={r['target']} validator={r['validator']}" for r in stale]
        (failures if strict else warnings).extend("stale current evidence: "+x for x in msgs)
    lines=[f"evidence records: {len(rows)}",f"current stale evidence: {len(stale)}"]
    if warnings: lines += ["warnings:"]+["  WARN "+x for x in warnings]
    if failures: lines += ["failures:"]+["  FAIL "+x for x in failures]
    return not failures,"\n".join(lines)


def cmd_verify(args):
    p=core("verify",*( ["--strict"] if args.strict else [] )); ok_core=p.returncode==0
    ok_evid,evid_report=verify_evidence(args.strict)
    report={"core":{"passed":ok_core,"output":p.stdout+p.stderr},"evidence":{"passed":ok_evid,"output":evid_report},"passed":ok_core and ok_evid}
    if args.json: print(json.dumps(report,indent=2,sort_keys=True))
    else:
        print((p.stdout+p.stderr).rstrip()); print("\nEOSV EVIDENCE INTEGRITY\n"+evid_report); print(f"\nEOSV RESULT: {'PASS' if report['passed'] else 'FAIL'}")
    if not report["passed"]: raise EosvError("EOS verification failed")


def cmd_validators(args):
    vals=merged_validators()
    if args.validators_command=="list":
        for k,v in sorted(vals.items()): print(f"{k:<24} {v.get('kind',''):<18} {v.get('description','')}")
    else:
        if args.name not in vals: raise EosvError(f"Unknown validator: {args.name}")
        print(json.dumps(vals[args.name],indent=2,sort_keys=True))


def cmd_validation(args):
    ps=profiles()
    if args.validation_command=="profiles":
        for name,p in sorted(ps.items()): print(f"{name:<18} required={','.join(p.get('required',[])) or '-'} optional={','.join(p.get('optional',[])) or '-'}")
    else:
        if args.name not in ps: raise EosvError(f"Unknown profile: {args.name}")
        print(json.dumps(ps[args.name],indent=2,sort_keys=True))


def cmd_validate(args): run_profile(args.target,args.profile,args.execution,args.covers or [],args.json)


def cmd_evidence(args):
    rows=read_tsv(EVID_REG)
    if args.evidence_command=="list":
        if args.target: rows=[r for r in rows if r.get("target")==args.target or r.get("execution")==args.target]
        if not args.all: rows=[r for r in rows if r.get("status")!="SUPERSEDED"]
        if args.json: print(json.dumps(rows,indent=2,sort_keys=True)); return
        for r in rows: print(f"{r['id']:<10} {r['status']:<11} {r['result']:<8} {r['validator']:<24} target={r['target']} exec={r['execution'] or '-'}")
    elif args.evidence_command=="show":
        row=evidence_row(args.evidence_id); data=load_json(EOS/"evidence"/f"{args.evidence_id}.json",{})
        print(json.dumps({"registry":row,"machine":data,"links":[r for r in read_tsv(LINK_REG) if r.get("evidence_id")==args.evidence_id]},indent=2,sort_keys=True))
    elif args.evidence_command=="link":
        evidence_row(args.evidence_id)
        links=read_tsv(LINK_REG); relation=args.relation
        for ref in args.references:
            if not re.fullmatch(r"(?:AC-[A-Z0-9][A-Z0-9-]*|REQ-[A-Z0-9][A-Z0-9-]*|SPEC-[A-Z0-9][A-Z0-9-]*|ADR-\d{4}|QA-[A-Z0-9][A-Z0-9-]*|CAP-[A-Z0-9][A-Z0-9-]*)",ref): raise EosvError(f"Unsupported evidence reference: {ref}")
            if not any(x.get("evidence_id")==args.evidence_id and x.get("reference")==ref and x.get("relation")==relation for x in links):
                links.append({"evidence_id":args.evidence_id,"reference":ref,"relation":relation,"created":now_iso(),"actor":args.actor or os.environ.get("USER","unknown")})
        write_tsv(LINK_REG,LINK_FIELDS,links); append_event("EVIDENCE_LINKED",args.evidence_id,action="link",metadata={"references":args.references,"relation":relation})
        print(f"Linked {args.evidence_id} to {', '.join(args.references)}")
    elif args.evidence_command=="coverage":
        target=args.target; wp=target
        if target.startswith("EXEC-"):
            er=exec_row(target); wp=er.get("target","") if er else ""
        criteria,unidentified=criteria_for_wp(wp); refs=[]
        p=artifact_path(wp)
        if p: refs=[x for x in references_from(p) if x.startswith(("REQ-","SPEC-","ADR-","QA-","CAP-"))]
        relevant=[r for r in rows if r.get("target")==wp and r.get("status")=="VALIDATED"]
        covered=set().union(*(evidence_covers(r) for r in relevant)) if relevant else set()
        items=[{"id":cid,"text":text,"covered":cid in covered} for cid,text in criteria]
        ref_items=[{"id":rid,"covered":rid in covered} for rid in refs]
        denom=len(items)+len(ref_items); hit=sum(1 for x in items+ref_items if x["covered"]); score=100.0 if denom==0 else 100*hit/denom
        report={"target":wp,"criteria":items,"unidentified_checklist_items":unidentified,"governing_references":ref_items,"validated_evidence":[r["id"] for r in relevant],"coverage_score":score}
        if args.json: print(json.dumps(report,indent=2,sort_keys=True))
        else:
            print(f"EVIDENCE COVERAGE — {wp}\nscore: {score:.1f}%\n")
            for x in items: print(f"{'COVERED' if x['covered'] else 'MISSING':<8} {x['id']} {x['text']}")
            for x in ref_items: print(f"{'COVERED' if x['covered'] else 'MISSING':<8} {x['id']}")
            if unidentified: print(f"WARN: {unidentified} checklist item(s) lack stable AC-* identifiers")
    elif args.evidence_command=="audit":
        report,failures=audit_evidence(mutate=True)
        if args.json: print(json.dumps(report,indent=2,sort_keys=True))
        else:
            for r in report: print(f"{r['id']:<10} {r['status']:<11} {'; '.join(r['issues']) or 'OK'}")
        if failures: raise EosvError("Evidence audit found integrity failures")


def cmd_performance(args):
    if args.performance_command=="list":
        rows=performance_rows(); print(json.dumps(rows,indent=2,sort_keys=True) if args.json else "\n".join(f"{r['id']} {r['name']}={r['baseline']} {r['unit']} direction={r['direction']} tolerance={r['tolerance']} target={r['target'] or '-'}" for r in rows)); return
    if args.performance_command=="record":
        rows=performance_rows(); existing=next((r for r in rows if r.get("name")==args.name and r.get("target")==args.target),None); now=now_iso()
        if existing: existing.update({"unit":args.unit,"direction":args.direction,"baseline":str(args.value),"tolerance":str(args.tolerance),"updated":now}); row=existing
        else:
            pid=f"PERF-{max([int(r['id'].split('-')[1]) for r in rows if re.fullmatch(r'PERF-\d{4}',r.get('id',''))] or [0])+1:04d}"; row={"id":pid,"name":args.name,"target":args.target,"unit":args.unit,"direction":args.direction,"baseline":str(args.value),"tolerance":str(args.tolerance),"created":now,"updated":now}; rows.append(row)
        write_tsv(PERF_REG,PERF_FIELDS,rows); append_event("PERFORMANCE_BASELINE_RECORDED",row["id"],entity_kind="PERF",action="record",metadata=row); print(json.dumps(row,indent=2,sort_keys=True) if args.json else f"Recorded {row['id']}: {args.name}={args.value} {args.unit}")
    else:
        row=find_perf(args.name,args.target)
        if not row: raise EosvError(f"No performance baseline for {args.name}")
        value=args.value
        if args.command:
            p=run([args.command],shell=True); 
            if p.returncode!=0: raise EosvError(p.stdout+p.stderr)
            try: value=float(p.stdout.strip())
            except ValueError: raise EosvError("Performance command stdout must be one numeric value")
        if value is None: raise EosvError("Provide VALUE or --command")
        ok,limit=performance_pass(row,float(value)); result={"name":args.name,"value":float(value),"baseline":float(row["baseline"]),"unit":row["unit"],"direction":row["direction"],"tolerance":float(row["tolerance"]),"limit":limit,"passed":ok}
        if args.json: print(json.dumps(result,indent=2,sort_keys=True))
        else: print(json.dumps(result,indent=2))
        # Create first-class performance evidence for target when supplied.
        if args.target:
            source_hash,_=source_fingerprint(args.target); env=environment_snapshot(ROOT); env_hash=canonical_hash(env); ev=create_evidence(target=args.target,exec_id="",profile="performance-check",vid=f"performance:{args.name}",kind="performance",result={"result":"PASSED" if ok else "FAILED","exit_code":0 if ok else 1,"command":args.command or "manual measurement","output":json.dumps(result),"details":result},source_hash=source_hash,env_hash=env_hash,env=env,covers=[]); print(f"evidence: {ev['id']}")
        if not ok: raise EosvError("Performance baseline check failed")


def cmd_security(args): run_profile(args.target,"security",args.execution,[],args.json)
def cmd_supply_chain(args):
    # Run only the supply-chain typed validator while retaining EVID semantics.
    wp,exec_id,cwd,_=context_for_target(args.target,args.execution); target=wp or args.target; sh,_=source_fingerprint(args.target,args.execution); env=environment_snapshot(cwd); eh=canonical_hash(env); result=builtin_supply_chain(cwd); ev=create_evidence(target=target,exec_id=exec_id,profile="supply-chain",vid="supply-chain",kind="supply-chain",result=result,source_hash=sh,env_hash=eh,env=env,covers=[]); report={"target":target,"execution":exec_id,"result":result["result"],"evidence":ev["id"],"details":result.get("details",{})}; print(json.dumps(report,indent=2,sort_keys=True) if args.json else f"Supply-chain inventory: {ev['id']} ({result['details'].get('count',0)} manifests)")


def build_parser():
    parser=argparse.ArgumentParser(prog="eos",description="EOSV Verification v2")
    sub=parser.add_subparsers(dest="command",required=True)
    p=sub.add_parser("validate"); p.add_argument("target"); p.add_argument("--profile",default="wp"); p.add_argument("--execution",default=""); p.add_argument("--covers",action="append",default=[]); p.add_argument("--json",action="store_true"); p.set_defaults(func=cmd_validate)
    p=sub.add_parser("verify"); p.add_argument("--strict",action="store_true"); p.add_argument("--json",action="store_true"); p.set_defaults(func=cmd_verify)
    v=sub.add_parser("validators"); vs=v.add_subparsers(dest="validators_command",required=True); p=vs.add_parser("list"); p.set_defaults(func=cmd_validators); p=vs.add_parser("show"); p.add_argument("name"); p.set_defaults(func=cmd_validators)
    v=sub.add_parser("validation"); vs=v.add_subparsers(dest="validation_command",required=True); p=vs.add_parser("profiles"); p.set_defaults(func=cmd_validation); p=vs.add_parser("show"); p.add_argument("name"); p.set_defaults(func=cmd_validation)
    e=sub.add_parser("evidence"); es=e.add_subparsers(dest="evidence_command",required=True)
    p=es.add_parser("list"); p.add_argument("target",nargs="?"); p.add_argument("--all",action="store_true"); p.add_argument("--json",action="store_true"); p.set_defaults(func=cmd_evidence)
    p=es.add_parser("show"); p.add_argument("evidence_id"); p.set_defaults(func=cmd_evidence)
    p=es.add_parser("coverage"); p.add_argument("target"); p.add_argument("--json",action="store_true"); p.set_defaults(func=cmd_evidence)
    p=es.add_parser("audit"); p.add_argument("--json",action="store_true"); p.set_defaults(func=cmd_evidence)
    p=es.add_parser("link"); p.add_argument("evidence_id"); p.add_argument("references",nargs="+"); p.add_argument("--relation",default="verifies"); p.add_argument("--actor",default=""); p.set_defaults(func=cmd_evidence)
    pf=sub.add_parser("performance"); ps=pf.add_subparsers(dest="performance_command",required=True)
    p=ps.add_parser("record"); p.add_argument("name"); p.add_argument("value",type=float); p.add_argument("--target",default=""); p.add_argument("--unit",default="unit"); p.add_argument("--direction",choices=("lower","higher","target"),default="lower"); p.add_argument("--tolerance",type=float,default=0.10); p.add_argument("--json",action="store_true"); p.set_defaults(func=cmd_performance)
    p=ps.add_parser("check"); p.add_argument("name"); p.add_argument("value",type=float,nargs="?"); p.add_argument("--target",default=""); p.add_argument("--command",default=""); p.add_argument("--json",action="store_true"); p.set_defaults(func=cmd_performance)
    p=ps.add_parser("list"); p.add_argument("--json",action="store_true"); p.set_defaults(func=cmd_performance)
    sc=sub.add_parser("security"); ss=sc.add_subparsers(dest="security_command",required=True); p=ss.add_parser("scan"); p.add_argument("target"); p.add_argument("--execution",default=""); p.add_argument("--json",action="store_true"); p.set_defaults(func=cmd_security)
    sp=sub.add_parser("supply-chain"); sps=sp.add_subparsers(dest="supply_chain_command",required=True); p=sps.add_parser("inventory"); p.add_argument("target"); p.add_argument("--execution",default=""); p.add_argument("--json",action="store_true"); p.set_defaults(func=cmd_supply_chain)
    return parser


def main():
    (ROOT/"engineering"/"evidence").mkdir(parents=True,exist_ok=True); (EOS/"evidence").mkdir(parents=True,exist_ok=True)
    args=build_parser().parse_args()
    try: args.func(args); return 0
    except EosvError as exc: print(f"ERROR: {exc}",file=sys.stderr); return 2
    except subprocess.CalledProcessError as exc: print(f"ERROR: command failed ({exc.returncode}): {exc}",file=sys.stderr); return exc.returncode or 1

if __name__=="__main__": raise SystemExit(main())
