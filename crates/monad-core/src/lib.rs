//! Deterministic, side-effect-free Monad workspace bootstrap semantics.
//!
//! Governed execution keeps compilation, untrusted serialization validation,
//! effect mediation, run-local recovery, verification, effect classification,
//! delegation, bounded workspace observation, and adapter-session transport as
//! distinct boundaries so transport or executor behavior cannot silently create
//! authority.

pub mod discovery;
pub mod harness;
pub mod harness_adapter;
pub mod harness_delegation;
pub mod harness_effects;
pub mod harness_gateway;
pub mod harness_runtime;
pub mod harness_validation;
pub mod harness_verification;
pub mod harness_workspace_read;
pub mod identity;
pub mod markdown;
pub mod workspace;
