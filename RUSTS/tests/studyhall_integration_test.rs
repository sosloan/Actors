//! Integration tests for the StudyHall sustainable economy model.
//!
//! Author: Steve Sloan (Prince Sloan)
//! System: Rust translation of the Lean 4 StudyHall specification.
//! Purpose: Verify the axioms and truth conditions for a sustainable
//!          "Learn-to-Earn" and "Play-to-Earn" educational economy.
//!
//! Each test corresponds directly to a definition, axiom, or theorem
//! from the Lean 4 source:
//!
//!   namespace StudyHall
//!     inductive Source  ...
//!     inductive Flow    ...
//!     def isRealValue   ...
//!     axiom no_self_minting ...
//!     def funded        ...
//!     def SustainableSystem ...
//!     theorem sustainability_truth ...
//!   end StudyHall

use actors_rust_components::{
    studyhall_find_funding_source, studyhall_funded, studyhall_is_real_value,
    studyhall_is_sustainable_system, studyhall_no_self_minting, StudyHallFlow, StudyHallSource,
};

// ── isRealValue tests ──────────────────────────────────────────────────────────

#[test]
fn test_institution_is_real_value() {
    assert!(studyhall_is_real_value(StudyHallSource::Institution));
}

#[test]
fn test_sponsor_is_real_value() {
    assert!(studyhall_is_real_value(StudyHallSource::Sponsor));
}

#[test]
fn test_philanthropy_is_real_value() {
    assert!(studyhall_is_real_value(StudyHallSource::Philanthropy));
}

#[test]
fn test_user_revenue_is_real_value() {
    assert!(studyhall_is_real_value(StudyHallSource::UserRevenue));
}

#[test]
fn test_treasury_seed_is_real_value() {
    assert!(studyhall_is_real_value(StudyHallSource::TreasurySeed));
}

/// Mirrors: ∀ s, isRealValue s
#[test]
fn test_all_sources_are_real_valued() {
    for source in StudyHallSource::ALL {
        assert!(
            studyhall_is_real_value(source),
            "Source {source:?} must be real-valued"
        );
    }
}

/// Exactly five canonical sources are defined.
#[test]
fn test_source_enum_is_exhaustive() {
    assert_eq!(StudyHallSource::ALL.len(), 5);
}

// ── no_self_minting tests ──────────────────────────────────────────────────────

/// A payout > 0 with no source violates the axiom.
#[test]
fn test_positive_payout_without_source_is_self_minting() {
    for flow in StudyHallFlow::ALL {
        assert!(
            !studyhall_no_self_minting(flow, 100, None),
            "Flow {flow:?} must not self-mint 100 tokens"
        );
    }
}

/// A zero-amount event with no source does not violate the axiom.
#[test]
fn test_zero_payout_without_source_is_fine() {
    for flow in StudyHallFlow::ALL {
        assert!(
            studyhall_no_self_minting(flow, 0, None),
            "Zero-amount event for {flow:?} must not be flagged as self-minting"
        );
    }
}

/// A payout backed by any real source is always permitted.
#[test]
fn test_positive_payout_with_real_source_is_valid() {
    for flow in StudyHallFlow::ALL {
        for source in StudyHallSource::ALL {
            assert!(
                studyhall_no_self_minting(flow, 500, Some(source)),
                "Flow {flow:?} funded by {source:?} must be valid"
            );
        }
    }
}

/// Every flow type must be blocked from self-minting.
#[test]
fn test_self_minting_detection_all_flows() {
    for flow in StudyHallFlow::ALL {
        assert!(
            !studyhall_no_self_minting(flow, 1, None),
            "Flow {flow:?} must not self-mint even 1 token"
        );
    }
}

/// Large payouts without a source always violate the axiom.
#[test]
fn test_large_payout_without_source_is_invalid() {
    assert!(!studyhall_no_self_minting(
        StudyHallFlow::PlayToEarn,
        10_000_000,
        None
    ));
}

/// Large payouts backed by a real source are permitted.
#[test]
fn test_large_payout_with_source_is_valid() {
    assert!(studyhall_no_self_minting(
        StudyHallFlow::LearnToEarn,
        10_000_000,
        Some(StudyHallSource::TreasurySeed)
    ));
}

// ── funded predicate tests ─────────────────────────────────────────────────────

// --- LearnToEarn ---

#[test]
fn test_learn_to_earn_funded_by_institution() {
    assert!(studyhall_funded(
        StudyHallFlow::LearnToEarn,
        StudyHallSource::Institution
    ));
}

#[test]
fn test_learn_to_earn_funded_by_sponsor() {
    assert!(studyhall_funded(
        StudyHallFlow::LearnToEarn,
        StudyHallSource::Sponsor
    ));
}

#[test]
fn test_learn_to_earn_funded_by_philanthropy() {
    assert!(studyhall_funded(
        StudyHallFlow::LearnToEarn,
        StudyHallSource::Philanthropy
    ));
}

#[test]
fn test_learn_to_earn_funded_by_user_revenue() {
    assert!(studyhall_funded(
        StudyHallFlow::LearnToEarn,
        StudyHallSource::UserRevenue
    ));
}

#[test]
fn test_learn_to_earn_funded_by_treasury_seed() {
    assert!(studyhall_funded(
        StudyHallFlow::LearnToEarn,
        StudyHallSource::TreasurySeed
    ));
}

// --- PlayToEarn ---

#[test]
fn test_play_to_earn_funded_by_sponsor() {
    assert!(studyhall_funded(
        StudyHallFlow::PlayToEarn,
        StudyHallSource::Sponsor
    ));
}

#[test]
fn test_play_to_earn_funded_by_user_revenue() {
    assert!(studyhall_funded(
        StudyHallFlow::PlayToEarn,
        StudyHallSource::UserRevenue
    ));
}

#[test]
fn test_play_to_earn_funded_by_treasury_seed() {
    assert!(studyhall_funded(
        StudyHallFlow::PlayToEarn,
        StudyHallSource::TreasurySeed
    ));
}

/// Institution does not fund PlayToEarn per the specification.
#[test]
fn test_play_to_earn_not_funded_by_institution() {
    assert!(!studyhall_funded(
        StudyHallFlow::PlayToEarn,
        StudyHallSource::Institution
    ));
}

/// Philanthropy does not fund PlayToEarn per the specification.
#[test]
fn test_play_to_earn_not_funded_by_philanthropy() {
    assert!(!studyhall_funded(
        StudyHallFlow::PlayToEarn,
        StudyHallSource::Philanthropy
    ));
}

// --- MentorReward ---

#[test]
fn test_mentor_reward_funded_by_institution() {
    assert!(studyhall_funded(
        StudyHallFlow::MentorReward,
        StudyHallSource::Institution
    ));
}

#[test]
fn test_mentor_reward_funded_by_user_revenue() {
    assert!(studyhall_funded(
        StudyHallFlow::MentorReward,
        StudyHallSource::UserRevenue
    ));
}

#[test]
fn test_mentor_reward_not_funded_by_sponsor() {
    assert!(!studyhall_funded(
        StudyHallFlow::MentorReward,
        StudyHallSource::Sponsor
    ));
}

#[test]
fn test_mentor_reward_not_funded_by_philanthropy() {
    assert!(!studyhall_funded(
        StudyHallFlow::MentorReward,
        StudyHallSource::Philanthropy
    ));
}

/// Treasury seed capital is not a direct MentorReward source —
/// mentor payouts must come from institutional or user-revenue channels.
#[test]
fn test_mentor_reward_not_funded_by_treasury_seed() {
    assert!(!studyhall_funded(
        StudyHallFlow::MentorReward,
        StudyHallSource::TreasurySeed
    ));
}

// --- Reserve ---

/// Reserve accepts every source — mirrors `| .Reserve, _ => True`.
#[test]
fn test_reserve_funded_by_all_sources() {
    for source in StudyHallSource::ALL {
        assert!(
            studyhall_funded(StudyHallFlow::Reserve, source),
            "Reserve must be fundable by {source:?}"
        );
    }
}

// --- Existence of at least one valid source per flow ---

/// Mirrors: ∀ f, ∃ s, funded f s
#[test]
fn test_every_flow_has_a_valid_funding_source() {
    for flow in StudyHallFlow::ALL {
        let source = studyhall_find_funding_source(flow);
        assert!(
            source.is_some(),
            "Flow {flow:?} has no valid funding source"
        );
        let s = source.unwrap();
        assert!(
            studyhall_funded(flow, s),
            "find_funding_source returned an invalid source {s:?} for {flow:?}"
        );
    }
}

// ── SustainableSystem / sustainability_truth theorem ──────────────────────────

/// The StudyHall economy satisfies all three sustainability conditions.
/// Mirrors: theorem sustainability_truth : SustainableSystem
#[test]
fn test_sustainable_system_holds() {
    assert!(studyhall_is_sustainable_system());
}

/// ∀ f, ∃ s, funded f s — every reward channel has a real funding source.
#[test]
fn test_condition_1_all_flows_funded() {
    for flow in StudyHallFlow::ALL {
        assert!(
            studyhall_find_funding_source(flow).is_some(),
            "Condition 1 failed: Flow {flow:?} has no funding source"
        );
    }
}

/// ∀ s, isRealValue s — every funding source is backed by fiat or tangible value.
#[test]
fn test_condition_2_all_sources_real() {
    for source in StudyHallSource::ALL {
        assert!(
            studyhall_is_real_value(source),
            "Condition 2 failed: Source {source:?} is not real-valued"
        );
    }
}

/// ∀ f, ¬(self-mint) — no flow can produce positive tokens without a real source.
#[test]
fn test_condition_3_no_self_minting() {
    for flow in StudyHallFlow::ALL {
        assert!(
            !studyhall_no_self_minting(flow, 1, None),
            "Condition 3 failed: Flow {flow:?} allows self-minting"
        );
    }
}

// ── Edge-case / negative integration tests ────────────────────────────────────

/// A zero-token event is economically neutral — not a mint.
#[test]
fn test_zero_value_payout_never_self_mints() {
    for flow in StudyHallFlow::ALL {
        assert!(studyhall_no_self_minting(flow, 0, None));
        assert!(studyhall_no_self_minting(
            flow,
            0,
            Some(StudyHallSource::Sponsor)
        ));
    }
}

/// Exactly four flow types exist in the specification.
#[test]
fn test_all_flows_enumerated() {
    assert_eq!(StudyHallFlow::ALL.len(), 4);
}

/// Institutions (schools/districts) are not listed as PlayToEarn funders —
/// this prevents misuse of educational funds for gaming rewards.
#[test]
fn test_institution_cannot_fund_play_to_earn() {
    assert!(!studyhall_funded(
        StudyHallFlow::PlayToEarn,
        StudyHallSource::Institution
    ));
}

/// Philanthropic funds are restricted to learning-oriented flows.
#[test]
fn test_philanthropy_cannot_fund_play_to_earn() {
    assert!(!studyhall_funded(
        StudyHallFlow::PlayToEarn,
        StudyHallSource::Philanthropy
    ));
}

/// Sponsors fund engagement (play/learn) not direct mentorship payouts.
#[test]
fn test_sponsor_cannot_fund_mentor_reward() {
    assert!(!studyhall_funded(
        StudyHallFlow::MentorReward,
        StudyHallSource::Sponsor
    ));
}

/// A circular economy where Flow outputs re-enter as Sources without
/// new external value is prevented by the no_self_minting axiom.
#[test]
fn test_circular_economy_is_blocked() {
    let circular_payout = 50_u64;
    let circular_source: Option<StudyHallSource> = None; // No external fiat entry
    assert!(!studyhall_no_self_minting(
        StudyHallFlow::LearnToEarn,
        circular_payout,
        circular_source
    ));
}

/// Introducing any real source resolves the circular dependency.
#[test]
fn test_fiat_entry_breaks_circular_dependency() {
    let circular_payout = 50_u64;
    let real_source = Some(StudyHallSource::UserRevenue);
    assert!(studyhall_no_self_minting(
        StudyHallFlow::LearnToEarn,
        circular_payout,
        real_source
    ));
}

/// The Reserve flow accepts any funding source as expected by the spec.
#[test]
fn test_reserve_is_universally_funded() {
    for source in StudyHallSource::ALL {
        assert!(
            studyhall_funded(StudyHallFlow::Reserve, source),
            "Reserve must accept {source:?}"
        );
    }
}

/// find_funding_source always returns a source that passes the funded predicate.
#[test]
fn test_find_funding_source_consistency() {
    for flow in StudyHallFlow::ALL {
        if let Some(source) = studyhall_find_funding_source(flow) {
            assert!(
                studyhall_funded(flow, source),
                "Returned source {source:?} must actually fund {flow:?}"
            );
        }
    }
}

/// A payout of exactly 1 token without any source is always self-minting.
#[test]
fn test_unit_payout_without_source_violates_axiom() {
    for flow in StudyHallFlow::ALL {
        assert!(
            !studyhall_no_self_minting(flow, 1, None),
            "Even a unit payout for {flow:?} without a source must be rejected"
        );
    }
}

/// A payout of exactly 1 token with any real source is always valid.
#[test]
fn test_unit_payout_with_any_real_source_is_valid() {
    for flow in StudyHallFlow::ALL {
        for source in StudyHallSource::ALL {
            assert!(
                studyhall_no_self_minting(flow, 1, Some(source)),
                "Unit payout for {flow:?} funded by {source:?} must be valid"
            );
        }
    }
}
