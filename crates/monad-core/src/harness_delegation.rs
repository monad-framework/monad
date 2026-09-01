//! Non-amplifying delegation controls for governed execution.
//!
//! A child executor may inherit authority already present in the parent
//! Execution Envelope. Broader authority is denied unless it is supplied as an
//! explicit additional grant by the accountable initiating actor. Parent
//! prohibitions remain absolute in this contract version.

use serde::Serialize;

use crate::harness::{ActorIdentity, CapabilityGrant, ExecutionEnvelope};

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct DelegationRequest {
    pub child_executor: ActorIdentity,
    pub requested_capabilities: Vec<CapabilityGrant>,
    pub requested_tools: Vec<String>,
}

#[derive(Clone, Debug, Default, Eq, PartialEq, Serialize)]
pub struct DelegationAuthorityContext {
    /// Actor asserting any authority beyond the parent envelope.
    pub accountable_actor_id: Option<String>,
    /// Explicit additional grants attributable to the accountable actor.
    pub additional_capability_grants: Vec<CapabilityGrant>,
    /// Explicit additional tool grants attributable to the accountable actor.
    pub additional_tool_grants: Vec<String>,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum DelegationDisposition {
    Allowed,
    DeniedAmplification,
    DeniedProhibition,
    DeniedUnaccountableGrant,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct DelegationDecision {
    pub disposition: DelegationDisposition,
    pub child_actor_id: String,
    pub denied_capability: Option<CapabilityGrant>,
    pub denied_tool: Option<String>,
    pub diagnostic: String,
}

pub fn assess_delegation(
    parent: &ExecutionEnvelope,
    request: &DelegationRequest,
    authority: &DelegationAuthorityContext,
) -> DelegationDecision {
    let accountable_additions_valid = authority
        .accountable_actor_id
        .as_deref()
        .is_some_and(|actor| actor == parent.initiating_actor().actor_id);

    for requested in &request.requested_capabilities {
        if contains_grant(parent.prohibited_capabilities(), requested) {
            return denied_capability(
                request,
                DelegationDisposition::DeniedProhibition,
                requested,
                "requested child capability is explicitly prohibited by the parent envelope",
            );
        }

        if contains_grant(parent.granted_capabilities(), requested) {
            continue;
        }

        if contains_grant(&authority.additional_capability_grants, requested) {
            if accountable_additions_valid {
                continue;
            }

            return denied_capability(
                request,
                DelegationDisposition::DeniedUnaccountableGrant,
                requested,
                "additional child authority is not attributable to the accountable initiating actor",
            );
        }

        return denied_capability(
            request,
            DelegationDisposition::DeniedAmplification,
            requested,
            "child delegation requested capability or scope not present in parent authority",
        );
    }

    for requested_tool in &request.requested_tools {
        if parent
            .allowed_tools()
            .iter()
            .any(|tool| tool == requested_tool)
        {
            continue;
        }

        if authority
            .additional_tool_grants
            .iter()
            .any(|tool| tool == requested_tool)
        {
            if accountable_additions_valid {
                continue;
            }

            return DelegationDecision {
                disposition: DelegationDisposition::DeniedUnaccountableGrant,
                child_actor_id: request.child_executor.actor_id.clone(),
                denied_capability: None,
                denied_tool: Some(requested_tool.clone()),
                diagnostic:
                    "additional child tool authority is not attributable to the accountable initiating actor"
                        .into(),
            };
        }

        return DelegationDecision {
            disposition: DelegationDisposition::DeniedAmplification,
            child_actor_id: request.child_executor.actor_id.clone(),
            denied_capability: None,
            denied_tool: Some(requested_tool.clone()),
            diagnostic: "child delegation requested tool not allowed by parent authority".into(),
        };
    }

    DelegationDecision {
        disposition: DelegationDisposition::Allowed,
        child_actor_id: request.child_executor.actor_id.clone(),
        denied_capability: None,
        denied_tool: None,
        diagnostic: "child authority is contained by parent authority or separately granted by accountable authority"
            .into(),
    }
}

fn contains_grant(grants: &[CapabilityGrant], requested: &CapabilityGrant) -> bool {
    grants.iter().any(|grant| grant == requested)
}

fn denied_capability(
    request: &DelegationRequest,
    disposition: DelegationDisposition,
    capability: &CapabilityGrant,
    diagnostic: &str,
) -> DelegationDecision {
    DelegationDecision {
        disposition,
        child_actor_id: request.child_executor.actor_id.clone(),
        denied_capability: Some(capability.clone()),
        denied_tool: None,
        diagnostic: diagnostic.into(),
    }
}

#[cfg(test)]
mod tests {
    use std::collections::BTreeMap;

    use super::*;
    use crate::harness::{ExecutionEnvelopeDraft, RunId, compile_execution_envelope};

    fn parent() -> ExecutionEnvelope {
        compile_execution_envelope(ExecutionEnvelopeDraft {
            schema_version: "0.1.0".into(),
            run_id: RunId("run-delegation-0001".into()),
            logical_time: "2026-09-01T12:00:00Z".into(),
            work_subject: "WP-HARNESS-C1-DELEGATION".into(),
            intent: "delegate bounded child work without authority amplification".into(),
            requested_outcome: "contained child authority".into(),
            governing_state_digest: "state-delegation".into(),
            governed_references: vec![],
            initiating_actor: ActorIdentity::new("human:owner", "engineering_owner"),
            executor: ActorIdentity::new("adapter:parent", "executor"),
            granted_capabilities: vec![CapabilityGrant::new(
                "workspace.read",
                "workspace/README.md",
            )],
            prohibited_capabilities: vec![CapabilityGrant::new("release.publish", "production")],
            allowed_tools: vec!["workspace".into()],
            environment_constraints: vec![],
            acceptance_criteria: vec![],
            verification_obligations: vec![],
            approval_gates: vec![],
            escalation_conditions: vec![],
            completion_criteria: vec![],
            resource_limits: BTreeMap::new(),
        })
    }

    fn request(capability: CapabilityGrant) -> DelegationRequest {
        DelegationRequest {
            child_executor: ActorIdentity::new("adapter:child", "executor"),
            requested_capabilities: vec![capability],
            requested_tools: vec!["workspace".into()],
        }
    }

    #[test]
    fn inherited_parent_authority_is_allowed() {
        let parent = parent();
        let request = request(CapabilityGrant::new(
            "workspace.read",
            "workspace/README.md",
        ));

        let decision = assess_delegation(&parent, &request, &DelegationAuthorityContext::default());

        assert_eq!(decision.disposition, DelegationDisposition::Allowed);
    }

    #[test]
    fn geh_cf_026_broader_child_authority_is_denied_without_accountable_grant() {
        let parent = parent();
        let request = request(CapabilityGrant::new(
            "workspace.write",
            "workspace/README.md",
        ));

        let decision = assess_delegation(&parent, &request, &DelegationAuthorityContext::default());

        assert_eq!(
            decision.disposition,
            DelegationDisposition::DeniedAmplification
        );
        assert_eq!(
            decision.denied_capability,
            Some(CapabilityGrant::new(
                "workspace.write",
                "workspace/README.md"
            ))
        );
    }

    #[test]
    fn separately_granted_authority_requires_accountable_actor() {
        let parent = parent();
        let requested = CapabilityGrant::new("workspace.write", "workspace/README.md");
        let request = request(requested.clone());
        let authority = DelegationAuthorityContext {
            accountable_actor_id: Some("adapter:parent".into()),
            additional_capability_grants: vec![requested],
            additional_tool_grants: vec![],
        };

        let decision = assess_delegation(&parent, &request, &authority);

        assert_eq!(
            decision.disposition,
            DelegationDisposition::DeniedUnaccountableGrant
        );
    }

    #[test]
    fn accountable_actor_may_separately_grant_non_prohibited_authority() {
        let parent = parent();
        let requested = CapabilityGrant::new("workspace.write", "workspace/README.md");
        let request = request(requested.clone());
        let authority = DelegationAuthorityContext {
            accountable_actor_id: Some("human:owner".into()),
            additional_capability_grants: vec![requested],
            additional_tool_grants: vec![],
        };

        let decision = assess_delegation(&parent, &request, &authority);

        assert_eq!(decision.disposition, DelegationDisposition::Allowed);
    }

    #[test]
    fn parent_prohibition_remains_absolute_even_with_additional_grant() {
        let parent = parent();
        let requested = CapabilityGrant::new("release.publish", "production");
        let request = DelegationRequest {
            child_executor: ActorIdentity::new("adapter:child", "executor"),
            requested_capabilities: vec![requested.clone()],
            requested_tools: vec!["release".into()],
        };
        let authority = DelegationAuthorityContext {
            accountable_actor_id: Some("human:owner".into()),
            additional_capability_grants: vec![requested],
            additional_tool_grants: vec!["release".into()],
        };

        let decision = assess_delegation(&parent, &request, &authority);

        assert_eq!(
            decision.disposition,
            DelegationDisposition::DeniedProhibition
        );
    }
}
