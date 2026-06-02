"""Command-line interface for harness sensors."""

from __future__ import annotations

import argparse
import json
import shlex
import shutil
from collections.abc import Sequence
from pathlib import Path

from harness_sensors.config import RuntimeConfig, load_runtime_config
from harness_sensors.evals import discover_eval_cases, render_eval_report, run_eval_cases
from harness_sensors.evidence import collect_evidence
from harness_sensors.integrations.agent_md_install import install_target_template
from harness_sensors.integrations.continue_export import export_continue_checks
from harness_sensors.reporters import ReportFormat
from harness_sensors.runner import SensorRunner
from harness_sensors.schema_loader import load_schema
from harness_sensors.sensor_card import SensorCardError, default_sensor_dir, discover_sensor_cards


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI."""

    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except SensorCardError as exc:
        print(f"sensor-card error: {exc}")
        return 2
    except (OSError, ValueError, KeyError) as exc:
        print(f"error: {exc}")
        return 1


def build_parser() -> argparse.ArgumentParser:
    """Build the top-level argument parser."""

    parser = argparse.ArgumentParser(prog="harness_sensors")
    parser.set_defaults(func=lambda _args: 0)
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor = subparsers.add_parser(
        "doctor", help="validate local sensor setup and target harness files"
    )
    _add_common_repo_args(doctor)
    doctor.add_argument("--strict", action="store_true")
    doctor.add_argument("--json", action="store_true", dest="json_output")
    doctor.set_defaults(func=_doctor)

    collect = subparsers.add_parser("collect", help="collect an evidence bundle")
    _add_common_repo_args(collect)
    collect.add_argument("--out", type=Path, default=None)
    collect.add_argument("--run-checks", action="store_true")
    collect.set_defaults(func=_collect)

    render = subparsers.add_parser("render", help="render one sensor prompt")
    _add_common_repo_args(render)
    render.add_argument("--sensor", required=True)
    render.add_argument("--out", type=Path, default=None)
    render.add_argument("--run-checks", action="store_true")
    render.set_defaults(func=_render)

    run = subparsers.add_parser("run", help="run sensors and write a report")
    _add_common_repo_args(run)
    group = run.add_mutually_exclusive_group(required=True)
    group.add_argument("--sensor")
    group.add_argument("--all", action="store_true")
    run.add_argument(
        "--format", choices=["markdown", "jsonl", "github", "agent"], default="markdown"
    )
    run.add_argument("--out", type=Path, default=None)
    run.add_argument("--run-checks", action="store_true")
    run.set_defaults(func=_run)

    install = subparsers.add_parser("install", help="install target-repo harness templates")
    install.add_argument("--repo", type=Path, required=True)
    install.add_argument("--profile", choices=["minimal"], default="minimal")
    install.add_argument("--force", action="store_true")
    install.set_defaults(func=_install)

    export = subparsers.add_parser("export", help="export integration assets")
    export_sub = export.add_subparsers(dest="export_command", required=True)
    export_continue = export_sub.add_parser("continue", help="export Continue-style checks")
    export_continue.add_argument("--repo", type=Path, required=True)
    export_continue.add_argument("--out", type=Path, default=None)
    export_continue.set_defaults(func=_export_continue)

    eval_parser = subparsers.add_parser("eval", help="run offline structural eval cases")
    eval_group = eval_parser.add_mutually_exclusive_group(required=True)
    eval_group.add_argument("--case", dest="case_name")
    eval_group.add_argument("--all", action="store_true")
    eval_parser.add_argument("--evals-dir", type=Path, default=None)
    eval_parser.add_argument("--sensors-dir", type=Path, default=None)
    eval_parser.add_argument("--json", action="store_true", dest="json_output")
    eval_parser.add_argument("--out", type=Path, default=None)
    eval_parser.set_defaults(func=_eval)

    return parser


def _add_common_repo_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--sensors-dir", type=Path, default=None)


def _load_runner(args: argparse.Namespace) -> SensorRunner:
    config = load_runtime_config(args.config)
    return SensorRunner(sensor_dir=args.sensors_dir or default_sensor_dir(), config=config)


def _doctor(args: argparse.Namespace) -> int:
    repo = args.repo.resolve()
    cards = discover_sensor_cards(args.sensors_dir or default_sensor_dir())
    config = load_runtime_config(args.config)
    expected_harness_files = [
        repo / config.target.harness_dir / "feature_list.json",
        repo / config.target.harness_dir / "progress.md",
        repo / config.target.harness_dir / "decisions.md",
        repo / config.target.harness_dir / "sprint_contract.md",
        repo / config.target.harness_dir / "quality_score.md",
    ]
    missing = [path for path in expected_harness_files if not path.exists()]
    issues = [f"missing target harness file: {path}" for path in missing]
    issues.extend(_doctor_docs_issues(repo, config.target.docs_paths))
    issues.extend(_doctor_command_issues(config.target.test_commands))
    issues.extend(_doctor_command_issues(config.target.build_commands))
    issues.extend(_doctor_command_issues(config.target.lint_commands))
    issues.extend(_doctor_command_issues(config.target.runtime_commands))
    issues.extend(_doctor_command_issues(config.target.health_check_commands))
    issues.extend(_doctor_command_issues(config.target.e2e_commands))
    issues.extend(_doctor_provider_issues(config))
    issues.extend(_doctor_schema_issues())

    report = {
        "sensor_cards": len(cards),
        "target_repo": str(repo),
        "provider": config.provider.name,
        "strict": bool(args.strict),
        "issues": issues,
        "ok": not issues,
    }
    if args.json_output:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"validated {len(cards)} sensor cards")
        print(f"target repo: {repo}")
        if missing:
            print("missing target harness files:")
            for path in missing:
                print(f"- {path}")
        else:
            print("target harness files present")
        if issues:
            print("doctor issues:")
            for issue in issues:
                print(f"- {issue}")
        print(f"provider: {config.provider.name}")
    return 1 if args.strict and issues else 0


def _doctor_docs_issues(repo: Path, docs_paths: list[str]) -> list[str]:
    issues: list[str] = []
    for configured_path in docs_paths:
        if not (repo / configured_path).exists():
            issues.append(f"configured docs path does not exist: {configured_path}")
    return issues


def _doctor_command_issues(commands: list[str]) -> list[str]:
    issues: list[str] = []
    for command in commands:
        parts = shlex.split(command)
        if parts and shutil.which(parts[0]) is None:
            issues.append(f"configured command is unavailable: {command}")
    return issues


def _doctor_provider_issues(config: RuntimeConfig) -> list[str]:
    provider = config.provider
    if provider.name == "openai" and provider.model is None:
        return ["openai provider requires model"]
    if provider.name == "anthropic" and provider.model is None:
        return ["anthropic provider requires model"]
    if provider.name == "local":
        issues: list[str] = []
        if provider.model is None:
            issues.append("local provider requires model")
        if provider.endpoint is None:
            issues.append("local provider requires endpoint")
        return issues
    return []


def _doctor_schema_issues() -> list[str]:
    issues: list[str] = []
    for schema_name in [
        "sensor-card.schema.json",
        "sensor-result.schema.json",
        "evidence-bundle.schema.json",
    ]:
        try:
            load_schema(schema_name)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            issues.append(f"schema could not be loaded: {schema_name}: {exc}")
    return issues


def _collect(args: argparse.Namespace) -> int:
    config = load_runtime_config(args.config)
    bundle = collect_evidence(args.repo, config, run_checks=bool(args.run_checks))
    out = args.out or (args.repo / config.target.evidence_dir / "latest" / "evidence.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(bundle.model_dump(mode="json"), indent=2, sort_keys=True), encoding="utf-8"
    )
    print(out)
    return 0


def _render(args: argparse.Namespace) -> int:
    runner = _load_runner(args)
    bundle = runner.collect(args.repo, run_checks=bool(args.run_checks))
    prompt = runner.render_prompt(args.sensor, bundle)
    out = args.out or (args.repo / runner.config.target.prompt_dir / f"{args.sensor}.prompt.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(prompt, encoding="utf-8")
    print(out)
    return 0


def _run(args: argparse.Namespace) -> int:
    runner = _load_runner(args)
    sensor_ids = runner.enabled_sensor_ids() if args.all else [args.sensor]
    bundle, results = runner.run_many(
        args.repo, sensor_ids=sensor_ids, run_checks=bool(args.run_checks)
    )
    output_format: ReportFormat = args.format
    extension = "jsonl" if output_format == "jsonl" else "md"
    out = args.out or (args.repo / runner.config.target.report_dir / f"harness-sensors.{extension}")
    runner.write_report(results, output_path=out, output_format=output_format, bundle=bundle)
    print(out)
    return 0


def _install(args: argparse.Namespace) -> int:
    written = install_target_template(args.repo.resolve(), force=bool(args.force))
    print(f"installed {len(written)} files for profile {args.profile}")
    for path in written:
        print(path)
    return 0


def _export_continue(args: argparse.Namespace) -> int:
    out_dir = args.out or (args.repo / ".continue" / "checks")
    written = export_continue_checks(sensor_dir=default_sensor_dir(), out_dir=out_dir)
    print(f"exported {len(written)} Continue checks")
    for path in written:
        print(path)
    return 0


def _eval(args: argparse.Namespace) -> int:
    case_names = discover_eval_cases(args.evals_dir) if args.all else [args.case_name]
    reports = run_eval_cases(
        case_names=case_names,
        evals_dir=args.evals_dir,
        sensor_dir=args.sensors_dir or default_sensor_dir(),
    )
    output = render_eval_report(reports, as_json=bool(args.json_output))
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output, encoding="utf-8")
        print(args.out)
    else:
        print(output, end="")
    return 0 if all(report.ok for report in reports) else 1
