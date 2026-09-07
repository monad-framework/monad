use std::{env, path::PathBuf, process::ExitCode};

use monad_codex_dogfood::{DogfoodPlan, run_dogfood};
use monad_codex_live_activation::LiveActivationPlan;
use monad_codex_runtime::ProcessJsonlTransport;
use serde_json::json;

struct CliConfig {
    plan: DogfoodPlan,
    codex: String,
}

fn main() -> ExitCode {
    match run(env::args().skip(1).collect()) {
        Ok(report) => {
            println!(
                "{}",
                serde_json::to_string_pretty(&report).expect("serializable dogfood report")
            );
            ExitCode::SUCCESS
        }
        Err(error) => {
            println!(
                "{}",
                serde_json::to_string_pretty(&json!({
                    "governed_execution_demonstrated": false,
                    "diagnostic": error,
                }))
                .expect("serializable dogfood diagnostic")
            );
            ExitCode::from(1)
        }
    }
}

fn run(arguments: Vec<String>) -> Result<monad_codex_dogfood::DogfoodReport, String> {
    let config = parse(arguments)?;
    let args = vec!["app-server".to_owned()];
    let certification = ProcessJsonlTransport::spawn(
        &config.codex,
        &args,
        Some(&config.plan.activation.provider_runtime_cwd),
    )
    .map_err(|error| error.to_string())?;
    let activation = ProcessJsonlTransport::spawn(
        &config.codex,
        &args,
        Some(&config.plan.activation.provider_runtime_cwd),
    )
    .map_err(|error| error.to_string())?;

    run_dogfood(certification, activation, &config.plan).map_err(|error| error.to_string())
}

fn parse(arguments: Vec<String>) -> Result<CliConfig, String> {
    let mut arguments = arguments.into_iter();
    if arguments.next().as_deref() != Some("run") {
        return Err("expected `run` command".into());
    }

    let mut profile = None;
    let mut provider_cwd = None;
    let mut forbidden_path = None;
    let mut forbidden_marker = None;
    let mut workspace_root = None;
    let mut read_path = None;
    let mut run_id = None;
    let mut logical_time = None;
    let mut governing_state_digest = None;
    let mut prompt = None;
    let mut max_bytes = 65_536_u64;
    let mut codex = "codex".to_owned();

    while let Some(argument) = arguments.next() {
        let value = |arguments: &mut std::vec::IntoIter<String>, name: &str| {
            arguments
                .next()
                .ok_or_else(|| format!("{name} requires a value"))
        };
        match argument.as_str() {
            "--profile" => profile = Some(value(&mut arguments, "--profile")?),
            "--provider-cwd" => {
                provider_cwd = Some(PathBuf::from(value(&mut arguments, "--provider-cwd")?))
            }
            "--forbidden-path" => {
                forbidden_path = Some(PathBuf::from(value(&mut arguments, "--forbidden-path")?))
            }
            "--forbidden-marker" => {
                forbidden_marker = Some(value(&mut arguments, "--forbidden-marker")?)
            }
            "--workspace-root" => {
                workspace_root = Some(PathBuf::from(value(&mut arguments, "--workspace-root")?))
            }
            "--read-path" => read_path = Some(value(&mut arguments, "--read-path")?),
            "--run-id" => run_id = Some(value(&mut arguments, "--run-id")?),
            "--logical-time" => logical_time = Some(value(&mut arguments, "--logical-time")?),
            "--governing-state-digest" => {
                governing_state_digest = Some(value(&mut arguments, "--governing-state-digest")?)
            }
            "--prompt" => prompt = Some(value(&mut arguments, "--prompt")?),
            "--max-bytes" => {
                let raw = value(&mut arguments, "--max-bytes")?;
                max_bytes = raw
                    .parse::<u64>()
                    .map_err(|_| "--max-bytes must be an unsigned integer".to_owned())?;
            }
            "--codex" => codex = value(&mut arguments, "--codex")?,
            _ => return Err(format!("unknown argument: {argument}")),
        }
    }

    let activation = LiveActivationPlan::new(
        profile.ok_or_else(|| "--profile is required".to_owned())?,
        provider_cwd.ok_or_else(|| "--provider-cwd is required".to_owned())?,
        forbidden_path.ok_or_else(|| "--forbidden-path is required".to_owned())?,
        forbidden_marker.ok_or_else(|| "--forbidden-marker is required".to_owned())?,
    );
    let plan = DogfoodPlan {
        activation,
        workspace_root: workspace_root.ok_or_else(|| "--workspace-root is required".to_owned())?,
        workspace_read_path: read_path.ok_or_else(|| "--read-path is required".to_owned())?,
        max_read_bytes: max_bytes,
        run_id: run_id.ok_or_else(|| "--run-id is required".to_owned())?,
        logical_time: logical_time.ok_or_else(|| "--logical-time is required".to_owned())?,
        governing_state_digest: governing_state_digest
            .ok_or_else(|| "--governing-state-digest is required".to_owned())?,
        prompt,
    };
    plan.validate().map_err(|error| error.to_string())?;

    Ok(CliConfig { plan, codex })
}

#[cfg(test)]
mod tests {
    use super::*;

    fn complete_arguments() -> Vec<String> {
        vec![
            "run".into(),
            "--profile".into(),
            "monad-geh-confinement".into(),
            "--provider-cwd".into(),
            "/tmp/provider".into(),
            "--forbidden-path".into(),
            "/tmp/workspace/.monad/sentinel".into(),
            "--forbidden-marker".into(),
            "MARKER".into(),
            "--workspace-root".into(),
            "/tmp/workspace".into(),
            "--read-path".into(),
            "README.md".into(),
            "--run-id".into(),
            "run-dogfood-0001".into(),
            "--logical-time".into(),
            "2026-09-07T16:00:00Z".into(),
            "--governing-state-digest".into(),
            "deadbeef".into(),
        ]
    }

    #[test]
    fn run_command_requires_explicit_governance_and_workspace_inputs() {
        let error = parse(vec!["run".into()]).err().unwrap();
        assert!(error.contains("--profile"));
    }

    #[test]
    fn complete_run_arguments_parse_without_launching_provider() {
        let config = parse(complete_arguments()).unwrap();
        assert_eq!(config.plan.workspace_read_path, "README.md");
        assert_eq!(config.plan.max_read_bytes, 65_536);
        assert_eq!(config.codex, "codex");
    }

    #[test]
    fn unknown_command_is_rejected_before_process_launch() {
        let error = parse(vec!["verify".into()]).err().unwrap();
        assert!(error.contains("expected `run`"));
    }
}
