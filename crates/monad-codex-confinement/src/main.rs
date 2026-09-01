use std::{env, path::PathBuf, process::ExitCode};

use monad_codex_confinement::{CodexConfinementVerifier, ConfinementProbePlan};
use monad_codex_runtime::ProcessJsonlTransport;
use serde_json::json;

fn main() -> ExitCode {
    match run(env::args().skip(1).collect()) {
        Ok(certificate) => {
            println!(
                "{}",
                serde_json::to_string_pretty(&certificate).expect("serializable certificate")
            );
            ExitCode::SUCCESS
        }
        Err(error) => {
            println!(
                "{}",
                serde_json::to_string_pretty(&json!({
                    "verified": false,
                    "diagnostic": error,
                }))
                .expect("serializable diagnostic")
            );
            ExitCode::from(1)
        }
    }
}

fn run(
    arguments: Vec<String>,
) -> Result<monad_codex_confinement::CodexConfinementCertificate, String> {
    let mut arguments = arguments.into_iter();
    if arguments.next().as_deref() != Some("verify") {
        return Err("expected `verify` command".into());
    }

    let mut profile = None;
    let mut provider_cwd = None;
    let mut forbidden_path = None;
    let mut forbidden_marker = None;
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
            "--codex" => codex = value(&mut arguments, "--codex")?,
            _ => return Err(format!("unknown argument: {argument}")),
        }
    }

    let profile = profile.ok_or_else(|| "--profile is required".to_owned())?;
    let provider_cwd = provider_cwd.ok_or_else(|| "--provider-cwd is required".to_owned())?;
    let forbidden_path =
        forbidden_path.ok_or_else(|| "--forbidden-path is required".to_owned())?;
    let forbidden_marker =
        forbidden_marker.ok_or_else(|| "--forbidden-marker is required".to_owned())?;

    let transport = ProcessJsonlTransport::spawn(
        codex,
        &["app-server".into()],
        Some(provider_cwd.as_path()),
    )
    .map_err(|error| error.to_string())?;
    let mut verifier = CodexConfinementVerifier::new(transport);
    verifier.initialize().map_err(|error| error.to_string())?;
    let plan = ConfinementProbePlan::linux_file_read(
        profile,
        provider_cwd,
        forbidden_path,
        forbidden_marker,
    );
    verifier.certify(&plan).map_err(|error| error.to_string())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn verify_command_requires_explicit_profile_and_paths() {
        let error = run(vec!["verify".into()]).unwrap_err();
        assert!(error.contains("--profile"));
    }

    #[test]
    fn unknown_command_is_rejected_before_process_launch() {
        let error = run(vec!["other".into()]).unwrap_err();
        assert!(error.contains("expected `verify`"));
    }
}
