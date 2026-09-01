//! Deterministic, side-effect-free Monad workspace bootstrap semantics.
//!
//! Governed execution keeps compilation, untrusted serialization validation,
//! and effect mediation as distinct boundaries so data transport cannot create
//! authority and an executor cannot bypass governance by choosing a backend.

pub mod discovery;
pub mod harness;
pub mod harness_gateway;
pub mod harness_validation;
pub mod identity;
pub mod markdown;
pub mod workspace;
