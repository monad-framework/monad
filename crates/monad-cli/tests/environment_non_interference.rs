use std::{
    fs,
    path::{Path, PathBuf},
    process::Command,
    time::{SystemTime, UNIX_EPOCH},
};

fn temp_dir(name: &str) -> PathBuf {
    let path = std::env::temp_dir().join(format!(
        "monad-cli-{name}-{}-{}",
        std::process::id(),
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .expect("clock")
            .as_nanos()
    ));

    fs::create_dir_all(&path).expect("create temporary repository");
    path
}

fn write_config(root: &Path) {
    fs::write(
        root.join("monad.toml"),
        r#"schema_version = 1

[project]
id = "fixture"
name = "Fixture"

[artifacts]
product = ["product/**/*.md"]

[ingestion]
network = false
execute_repository_code = false
"#,
    )
    .expect("write monad.toml");
}

fn bootstrap_with_environment(root: &Path, environment_value: &str) -> Vec<u8> {
    let output = Command::new(env!("CARGO_BIN_EXE_monad"))
        .arg("bootstrap")
        .arg("--root")
        .arg(root)
        .arg("--format")
        .arg("json")
        .env_clear()
        .env("MONAD_PROJECT_ID", environment_value)
        .env("MONAD_PROJECT_NAME", environment_value)
        .env("MONAD_EXCLUDE_PATHS", environment_value)
        .env("MONAD_INGESTION_NETWORK", environment_value)
        .output()
        .expect("run monad bootstrap");

    assert!(
        output.status.success(),
        "bootstrap failed:\nstdout:\n{}\nstderr:\n{}",
        String::from_utf8_lossy(&output.stdout),
        String::from_utf8_lossy(&output.stderr),
    );

    output.stdout
}

#[test]
fn semantic_configuration_is_independent_of_environment_variables() {
    let root = temp_dir("environment-non-interference");
    write_config(&root);

    let first = bootstrap_with_environment(&root, "environment-one");
    let second = bootstrap_with_environment(&root, "environment-two");

    assert_eq!(
        first, second,
        "semantic bootstrap output changed with ambient environment"
    );

    let text = String::from_utf8(first).expect("UTF-8 bootstrap output");

    assert!(text.contains("\"value\": \"fixture\""));
    assert!(text.contains("\"source\": \"monad.toml:project.id\""));

    fs::remove_dir_all(root).expect("remove temporary repository");
}
