# Development Tools

This directory contains tool configuration, wrappers, or project-owned helpers
that do not belong in ordinary runtime code. Tool choices support the project;
they do not become product architecture by accident.

## Selection criteria

Evaluate a tool by the problem it solves, maintained status, security model,
license, installation and update path, reproducibility, platform support,
automation interface, output stability, performance, total operating cost, and
exit strategy. Prefer a smaller coherent toolchain over overlapping utilities.

## Version policy

Pin versions needed for reproducible build, test, generation, migration, and
release behavior. Record the authoritative version in one place and automate
update checks. Updates are reviewed like code: release notes, compatibility,
security, generated diffs, and rollback are considered.

## Execution policy

Tools and plugins execute code with contributor or automation authority. Use
trusted sources, verify integrity, minimize permissions and network access, and
do not expose production credentials to formatting, linting, or untrusted
extension processes.

## Wrappers

Provide a project wrapper when it normalizes complex arguments, enforces safety,
or makes local and CI behavior identical. Wrappers should pass through useful
exit status, expose the underlying tool version, and avoid concealing failures.

## Removal

A tool is removed when its need disappears, maintenance or security becomes
unacceptable, or a simpler existing capability replaces it. Remove configuration,
caches, automation references, documentation, and dependency permissions as
part of the same change.
