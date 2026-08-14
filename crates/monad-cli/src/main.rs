use std::{env, path::PathBuf, process::ExitCode};

use monad_core::workspace::{BootstrapError, CliOverrides, Diagnostic, DiagnosticCode, bootstrap};
use serde_json::json;

fn main() -> ExitCode {
    match run(env::args().skip(1).collect()) {
        Ok(output) => {
            println!(
                "{}",
                serde_json::to_string_pretty(&output).expect("serializable output")
            );
            ExitCode::SUCCESS
        }
        Err(error) => {
            println!(
                "{}",
                serde_json::to_string_pretty(&json!({ "diagnostics": error.diagnostics() }))
                    .expect("serializable diagnostics")
            );
            ExitCode::from(1)
        }
    }
}

fn run(arguments: Vec<String>) -> Result<serde_json::Value, BootstrapError> {
    let mut arguments = arguments.into_iter();
    if matches!(arguments.next().as_deref(), Some("bootstrap")) {
    } else {
        return Err(command_error("expected `bootstrap` command"));
    }
    let mut root = None;
    let mut overrides = CliOverrides::default();
    while let Some(argument) = arguments.next() {
        let value = |arguments: &mut std::vec::IntoIter<String>, name: &str| {
            arguments
                .next()
                .ok_or_else(|| command_error(format!("{name} requires a value")))
        };
        match argument.as_str() {
            "--root" => root = Some(PathBuf::from(value(&mut arguments, "--root")?)),
            "--project-id" => overrides.project_id = Some(value(&mut arguments, "--project-id")?),
            "--project-name" => {
                overrides.project_name = Some(value(&mut arguments, "--project-name")?)
            }
            "--project-type" => {
                overrides.project_type = Some(value(&mut arguments, "--project-type")?)
            }
            "--exclude-path" => overrides
                .exclude_paths
                .get_or_insert_default()
                .push(value(&mut arguments, "--exclude-path")?),
            "--artifact" => {
                let item = value(&mut arguments, "--artifact")?;
                let (name, pattern) = item
                    .split_once('=')
                    .ok_or_else(|| command_error("--artifact must be NAME=PATTERN"))?;
                if name.is_empty() {
                    return Err(command_error("--artifact name must be non-empty"));
                }
                overrides
                    .artifact_roots
                    .entry(name.to_owned())
                    .or_insert_with(Vec::new)
                    .push(pattern.to_owned());
            }
            "--format" => {
                if value(&mut arguments, "--format")? != "json" {
                    return Err(command_error("only --format json is supported"));
                }
            }
            _ => return Err(command_error(format!("unknown argument: {argument}"))),
        }
    }
    let result = bootstrap(root.as_deref(), &overrides)?;
    serde_json::to_value(result)
        .map_err(|error| command_error(format!("cannot serialize bootstrap result: {error}")))
}

fn command_error(message: impl Into<String>) -> BootstrapError {
    BootstrapError::from_diagnostic(Diagnostic {
        code: DiagnosticCode::InvalidConfiguration,
        message: message.into(),
        location: Some("cli".to_owned()),
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn requires_bootstrap_command() {
        assert!(run(vec![]).is_err());
    }
}
