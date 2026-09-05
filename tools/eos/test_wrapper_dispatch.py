#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WRAPPER = ROOT / "scripts" / "eos"


def write_fake(path: Path, label: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "#!/usr/bin/env python3\n"
        "import os, sys\n"
        "from pathlib import Path\n"
        "log = Path(os.environ['EOS_DISPATCH_LOG'])\n"
        f"label = {label!r}\n"
        "args = sys.argv[1:]\n"
        "with log.open('a', encoding='utf-8') as f:\n"
        "    f.write(label + ':' + ' '.join(args) + '\\n')\n"
        "print(label + ' ' + ' '.join(args))\n"
        "fail_label = os.environ.get('EOS_FAIL_LABEL', '')\n"
        "fail_action = os.environ.get('EOS_FAIL_ACTION', '')\n"
        "action = args[0] if args else ''\n"
        "if label == 'canonical' and action == 'rollback-transaction' and os.environ.get('EOS_FAIL_ROLLBACK') == '1':\n"
        "    raise SystemExit(int(os.environ.get('EOS_ROLLBACK_FAIL_CODE', '12')))\n"
        "if label == fail_label and (not fail_action or action == fail_action):\n"
        "    raise SystemExit(int(os.environ.get('EOS_FAIL_CODE', '9')))\n",
        encoding="utf-8",
    )


def run_case(
    root: Path,
    args: list[str],
    env_overrides: dict[str, str] | None = None,
) -> tuple[int, list[str], str]:
    log = root / "dispatch.log"
    if log.exists():
        log.unlink()
    env = dict(os.environ)
    env["EOS_DISPATCH_LOG"] = str(log)
    if env_overrides:
        env.update(env_overrides)
    proc = subprocess.run(
        ["bash", str(root / "scripts" / "eos"), *args],
        cwd=root,
        env=env,
        text=True,
        capture_output=True,
    )
    lines = log.read_text(encoding="utf-8").splitlines() if log.exists() else []
    return proc.returncode, lines, proc.stdout + proc.stderr


def expect(label: str, actual: list[str], expected: list[str]) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="eos-wrapper-dispatch-") as tmp:
        root = Path(tmp)
        (root / "scripts").mkdir(parents=True)
        shutil.copy2(WRAPPER, root / "scripts" / "eos")
        (root / ".eos" / "cache").mkdir(parents=True)
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)

        write_fake(root / "tools" / "eos" / "canonical_state.py", "canonical")
        write_fake(root / "tools" / "eos" / "eos.py", "legacy")
        write_fake(root / "tools" / "eos" / "execution_v2.py", "execution")
        write_fake(root / "tools" / "eos" / "verification_v2.py", "verification")

        rc, lines, output = run_case(root, ["next"])
        if rc != 0:
            raise AssertionError(f"next failed: {output}")
        expect(
            "legacy dispatch",
            lines,
            ["canonical:pre -- next", "legacy:next", "canonical:post -- next"],
        )

        rc, lines, output = run_case(
            root,
            ["next"],
            {
                "EOS_FAIL_LABEL": "legacy",
                "EOS_FAIL_CODE": "7",
            },
        )
        if rc != 7:
            raise AssertionError(
                f"runtime failure should preserve runtime rc 7: {output}"
            )
        expect(
            "runtime failure rollback dispatch",
            lines,
            [
                "canonical:pre -- next",
                "legacy:next",
                "canonical:rollback-transaction --reason "
                "selected runtime exited with status 7 -- next",
            ],
        )

        rc, lines, output = run_case(
            root,
            ["next"],
            {
                "EOS_FAIL_LABEL": "canonical",
                "EOS_FAIL_ACTION": "post",
                "EOS_FAIL_CODE": "9",
            },
        )
        if rc != 9:
            raise AssertionError(
                f"post failure should preserve post rc 9: {output}"
            )
        expect(
            "post failure rollback dispatch",
            lines,
            [
                "canonical:pre -- next",
                "legacy:next",
                "canonical:post -- next",
                "canonical:rollback-transaction --reason "
                "canonical post-validation exited with status 9 -- next",
            ],
        )


        rc, lines, output = run_case(
            root,
            ["next"],
            {
                "EOS_FAIL_LABEL": "legacy",
                "EOS_FAIL_CODE": "7",
                "EOS_FAIL_ROLLBACK": "1",
                "EOS_ROLLBACK_FAIL_CODE": "12",
            },
        )

        if rc != 2:
            raise AssertionError(
                "rollback failure must fail closed with wrapper rc 2: "
                + output
            )

        if "explicit recovery is required" not in output:
            raise AssertionError(
                "rollback failure did not emit recovery-required diagnostic: "
                + output
            )

        expect(
            "rollback failure dispatch",
            lines,
            [
                "canonical:pre -- next",
                "legacy:next",
                "canonical:rollback-transaction --reason "
                "selected runtime exited with status 7 -- next",
            ],
        )

        rc, lines, output = run_case(root, ["verify", "--strict"])
        if rc != 0:
            raise AssertionError(f"verify failed: {output}")
        expect(
            "verification-v2 dispatch",
            lines,
            [
                "canonical:pre -- verify --strict",
                "verification:verify --strict",
                "canonical:post -- verify --strict",
            ],
        )

        rc, lines, output = run_case(root, ["codex", "WP-MVP-0001"])
        if rc != 0:
            raise AssertionError(f"codex failed: {output}")
        expect(
            "execution-v2 dispatch",
            lines,
            [
                "canonical:pre -- codex WP-MVP-0001",
                "execution:codex WP-MVP-0001",
                "canonical:post -- codex WP-MVP-0001",
            ],
        )

    print("EOS WRAPPER DISPATCH: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
