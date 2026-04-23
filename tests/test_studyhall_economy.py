#!/usr/bin/env python3
"""
Integration tests for the StudyHall sustainable economy model.

Author: Steve Sloan (Prince Sloan)
System: Python translation of the Lean 4 StudyHall specification.
Purpose: Verify the axioms and truth conditions for a sustainable
         "Learn-to-Earn" and "Play-to-Earn" educational economy.

Each test corresponds directly to a definition, axiom, or theorem
from the Lean 4 source:

  namespace StudyHall
    inductive Source  ...
    inductive Flow    ...
    def isRealValue   ...
    axiom no_self_minting ...
    def funded        ...
    def SustainableSystem ...
    theorem sustainability_truth ...
  end StudyHall
"""

import pytest
from enum import Enum, auto
from typing import Optional

# ---------------------------------------------------------------------------
# Domain model — mirrors the Lean 4 inductive types
# ---------------------------------------------------------------------------

class Source(Enum):
    """Funding origins that bring real value into the system."""
    Institution = auto()   # schools, universities, districts
    Sponsor = auto()       # corporations, NIL brands, partners
    Philanthropy = auto()  # nonprofit or donor foundations
    UserRevenue = auto()   # subscriptions, tutoring, or app fees
    TreasurySeed = auto()  # initial capital reserve (seed, DAO, investors)


class Flow(Enum):
    """Reward distribution channels."""
    LearnToEarn = auto()
    PlayToEarn = auto()
    MentorReward = auto()
    Reserve = auto()


# ---------------------------------------------------------------------------
# Lean 4 definitions translated to Python
# ---------------------------------------------------------------------------

def is_real_value(source: Source) -> bool:
    """
    Lean 4: def isRealValue (s : Source) : Prop
    Value exists only if fiat or real goods enter the system.
    Every known Source variant is real-valued.
    """
    return source in {
        Source.Institution,
        Source.Sponsor,
        Source.Philanthropy,
        Source.UserRevenue,
        Source.TreasurySeed,
    }


# Valid funding relationships — mirrors the Lean 4 `funded` match table.
_FUNDED: dict[Flow, set[Source]] = {
    Flow.LearnToEarn: {
        Source.Institution,
        Source.Sponsor,
        Source.Philanthropy,
        Source.UserRevenue,
        Source.TreasurySeed,
    },
    Flow.PlayToEarn: {
        Source.Sponsor,
        Source.UserRevenue,
        Source.TreasurySeed,
    },
    Flow.MentorReward: {
        Source.Institution,
        Source.UserRevenue,
    },
    Flow.Reserve: set(Source),  # Any source funds the reserve
}


def funded(flow: Flow, source: Source) -> bool:
    """
    Lean 4: def funded (f : Flow) (s : Source) : Prop
    Returns True iff `source` is a valid funder for `flow`.
    """
    return source in _FUNDED.get(flow, set())


def find_funding_source(flow: Flow) -> Optional[Source]:
    """
    Lean 4: ∀ f, ∃ s, funded f s
    Return any valid funding source for `flow`, or None if none exists.
    """
    sources = _FUNDED.get(flow, set())
    return next(iter(sources), None)


def no_self_minting(flow: Flow, amount: int, source: Optional[Source]) -> bool:
    """
    Lean 4: axiom no_self_minting : ∀ (t : Flow), ¬ (∃ v : Nat, v > 0 ∧ v originates_from t)
    Returns True (i.e. no violation) when the payout has a real source.
    A violation occurs when amount > 0 but source is None (self-generated).
    """
    if amount > 0 and source is None:
        return False   # Self-minting detected — axiom violated
    return True


def is_sustainable_system() -> bool:
    """
    Lean 4: def SustainableSystem : Prop
             (∀ f, ∃ s, funded f s)
           ∧ (∀ s, isRealValue s)
           ∧ (∀ f, ¬ self-mint f)

    Returns True iff all three conditions hold:
      1. Every flow has at least one valid real funding source.
      2. Every source is real-valued (fiat or tangible goods).
      3. No flow can produce a positive payout without an external source.
    """
    # Condition 1: every flow has at least one valid funding source
    all_flows_funded = all(find_funding_source(f) is not None for f in Flow)

    # Condition 2: every source is real-valued
    all_sources_real = all(is_real_value(s) for s in Source)

    # Condition 3: no flow is capable of self-minting positive amounts
    #   Verify that every flow violates the axiom when given a non-zero
    #   amount and no real funding source (i.e. self-minting is blocked).
    no_self_mint = all(not no_self_minting(f, 1, None) for f in Flow)

    return all_flows_funded and all_sources_real and no_self_mint


# ---------------------------------------------------------------------------
# isRealValue tests
# ---------------------------------------------------------------------------

class TestIsRealValue:
    """All Source variants must represent real, fiat-backed value."""

    @pytest.mark.integration
    def test_institution_is_real(self):
        assert is_real_value(Source.Institution)

    @pytest.mark.integration
    def test_sponsor_is_real(self):
        assert is_real_value(Source.Sponsor)

    @pytest.mark.integration
    def test_philanthropy_is_real(self):
        assert is_real_value(Source.Philanthropy)

    @pytest.mark.integration
    def test_user_revenue_is_real(self):
        assert is_real_value(Source.UserRevenue)

    @pytest.mark.integration
    def test_treasury_seed_is_real(self):
        assert is_real_value(Source.TreasurySeed)

    @pytest.mark.integration
    def test_all_sources_are_real(self):
        """Mirrors: ∀ s, isRealValue s"""
        for source in Source:
            assert is_real_value(source), f"Source {source} must be real-valued"

    @pytest.mark.integration
    def test_source_enum_is_exhaustive(self):
        """All five canonical sources are present."""
        assert len(list(Source)) == 5


# ---------------------------------------------------------------------------
# no_self_minting tests
# ---------------------------------------------------------------------------

class TestNoSelfMinting:
    """Tokens cannot be generated without a prior real funding source."""

    @pytest.mark.integration
    def test_positive_payout_requires_source(self):
        """A payout > 0 with no source violates the axiom."""
        for flow in Flow:
            assert not no_self_minting(flow, 100, None), (
                f"Flow {flow} must not self-mint 100 tokens"
            )

    @pytest.mark.integration
    def test_zero_payout_without_source_is_fine(self):
        """A zero-amount event with no source does not violate the axiom."""
        for flow in Flow:
            assert no_self_minting(flow, 0, None)

    @pytest.mark.integration
    def test_positive_payout_with_real_source_is_valid(self):
        """A payout backed by any real source is always permitted."""
        for flow in Flow:
            for source in Source:
                assert no_self_minting(flow, 500, source), (
                    f"Flow {flow} funded by {source} must be valid"
                )

    @pytest.mark.integration
    def test_self_minting_detection_all_flows(self):
        """Every flow type must be blocked from self-minting."""
        for flow in Flow:
            assert not no_self_minting(flow, 1, None)


# ---------------------------------------------------------------------------
# funded predicate tests
# ---------------------------------------------------------------------------

class TestFunded:
    """Every flow must be fundable, and funding relationships must be correct."""

    # --- LearnToEarn ---

    @pytest.mark.integration
    def test_learn_to_earn_funded_by_institution(self):
        assert funded(Flow.LearnToEarn, Source.Institution)

    @pytest.mark.integration
    def test_learn_to_earn_funded_by_sponsor(self):
        assert funded(Flow.LearnToEarn, Source.Sponsor)

    @pytest.mark.integration
    def test_learn_to_earn_funded_by_philanthropy(self):
        assert funded(Flow.LearnToEarn, Source.Philanthropy)

    @pytest.mark.integration
    def test_learn_to_earn_funded_by_user_revenue(self):
        assert funded(Flow.LearnToEarn, Source.UserRevenue)

    @pytest.mark.integration
    def test_learn_to_earn_funded_by_treasury_seed(self):
        assert funded(Flow.LearnToEarn, Source.TreasurySeed)

    # --- PlayToEarn ---

    @pytest.mark.integration
    def test_play_to_earn_funded_by_sponsor(self):
        assert funded(Flow.PlayToEarn, Source.Sponsor)

    @pytest.mark.integration
    def test_play_to_earn_funded_by_user_revenue(self):
        assert funded(Flow.PlayToEarn, Source.UserRevenue)

    @pytest.mark.integration
    def test_play_to_earn_funded_by_treasury_seed(self):
        assert funded(Flow.PlayToEarn, Source.TreasurySeed)

    @pytest.mark.integration
    def test_play_to_earn_not_funded_by_institution(self):
        """Institution does not fund PlayToEarn per the specification."""
        assert not funded(Flow.PlayToEarn, Source.Institution)

    @pytest.mark.integration
    def test_play_to_earn_not_funded_by_philanthropy(self):
        """Philanthropy does not fund PlayToEarn per the specification."""
        assert not funded(Flow.PlayToEarn, Source.Philanthropy)

    # --- MentorReward ---

    @pytest.mark.integration
    def test_mentor_reward_funded_by_institution(self):
        assert funded(Flow.MentorReward, Source.Institution)

    @pytest.mark.integration
    def test_mentor_reward_funded_by_user_revenue(self):
        assert funded(Flow.MentorReward, Source.UserRevenue)

    @pytest.mark.integration
    def test_mentor_reward_not_funded_by_sponsor(self):
        assert not funded(Flow.MentorReward, Source.Sponsor)

    @pytest.mark.integration
    def test_mentor_reward_not_funded_by_philanthropy(self):
        assert not funded(Flow.MentorReward, Source.Philanthropy)

    @pytest.mark.integration
    def test_mentor_reward_not_funded_by_treasury_seed(self):
        assert not funded(Flow.MentorReward, Source.TreasurySeed)

    # --- Reserve ---

    @pytest.mark.integration
    def test_reserve_funded_by_all_sources(self):
        """Reserve accepts every source — mirrors `| .Reserve, _ => True`."""
        for source in Source:
            assert funded(Flow.Reserve, source), (
                f"Reserve must be fundable by {source}"
            )

    # --- Existence of at least one valid source per flow ---

    @pytest.mark.integration
    def test_every_flow_has_a_valid_funding_source(self):
        """Mirrors: ∀ f, ∃ s, funded f s"""
        for flow in Flow:
            source = find_funding_source(flow)
            assert source is not None, (
                f"Flow {flow} has no valid funding source"
            )
            assert funded(flow, source), (
                f"find_funding_source returned an invalid source {source} for {flow}"
            )


# ---------------------------------------------------------------------------
# SustainableSystem / sustainability_truth theorem
# ---------------------------------------------------------------------------

class TestSustainabilityTruth:
    """
    Mirrors the Lean 4 theorem:
      theorem sustainability_truth : SustainableSystem
    """

    @pytest.mark.integration
    def test_sustainable_system_holds(self):
        """The StudyHall economy satisfies all three sustainability conditions."""
        assert is_sustainable_system()

    @pytest.mark.integration
    def test_condition_1_all_flows_funded(self):
        """∀ f, ∃ s, funded f s — every reward channel has a real funding source."""
        for flow in Flow:
            assert find_funding_source(flow) is not None, (
                f"Condition 1 failed: Flow {flow} has no funding source"
            )

    @pytest.mark.integration
    def test_condition_2_all_sources_real(self):
        """∀ s, isRealValue s — every funding source is backed by fiat or tangible value."""
        for source in Source:
            assert is_real_value(source), (
                f"Condition 2 failed: Source {source} is not real-valued"
            )

    @pytest.mark.integration
    def test_condition_3_no_self_minting(self):
        """∀ f, ¬(self-mint) — no flow can produce positive tokens without a real source."""
        for flow in Flow:
            assert not no_self_minting(flow, 1, None), (
                f"Condition 3 failed: Flow {flow} allows self-minting"
            )

    @pytest.mark.integration
    def test_sustainability_broken_when_flow_unfunded(self):
        """If a flow loses all funding sources the system is no longer sustainable."""
        # Temporarily shadow LearnToEarn funding with empty set
        original = _FUNDED[Flow.LearnToEarn]
        _FUNDED[Flow.LearnToEarn] = set()
        try:
            assert not is_sustainable_system()
        finally:
            _FUNDED[Flow.LearnToEarn] = original

    @pytest.mark.integration
    def test_sustainability_still_holds_after_restore(self):
        """After restoring funding the system returns to sustainable state."""
        assert is_sustainable_system()


# ---------------------------------------------------------------------------
# Edge-case / negative integration tests
# ---------------------------------------------------------------------------

class TestEdgeCases:
    """Boundary conditions and adversarial scenarios."""

    @pytest.mark.integration
    def test_zero_value_payout_never_self_mints(self):
        """A zero-token event is economically neutral — not a mint."""
        for flow in Flow:
            for source in [None, Source.Sponsor]:
                assert no_self_minting(flow, 0, source)

    @pytest.mark.integration
    def test_large_payout_with_source_is_valid(self):
        """Large payouts are acceptable when backed by a real source."""
        assert no_self_minting(Flow.LearnToEarn, 10_000_000, Source.TreasurySeed)

    @pytest.mark.integration
    def test_large_payout_without_source_is_invalid(self):
        """Large payouts without a source always violate the axiom."""
        assert not no_self_minting(Flow.PlayToEarn, 10_000_000, None)

    @pytest.mark.integration
    def test_funding_relationship_is_not_reflexive(self):
        """A Flow is not a Source — the concepts are disjoint."""
        assert Flow.LearnToEarn not in set(Source)

    @pytest.mark.integration
    def test_all_flows_enumerated(self):
        """Exactly four flow types exist in the specification."""
        assert len(list(Flow)) == 4

    @pytest.mark.integration
    def test_funded_rejects_unknown_flow_gracefully(self):
        """
        The funded lookup table must cover every Flow member;
        no KeyError should be raised for any canonical flow.
        """
        for flow in Flow:
            # Should not raise
            _ = _FUNDED[flow]

    @pytest.mark.integration
    def test_institution_cannot_fund_play_to_earn(self):
        """
        Institutions (schools/districts) are not listed as PlayToEarn funders —
        this prevents misuse of educational funds for gaming rewards.
        """
        assert not funded(Flow.PlayToEarn, Source.Institution)

    @pytest.mark.integration
    def test_philanthropy_cannot_fund_play_to_earn(self):
        """Philanthropic funds are restricted to learning-oriented flows."""
        assert not funded(Flow.PlayToEarn, Source.Philanthropy)

    @pytest.mark.integration
    def test_treasury_seed_cannot_fund_mentor_reward_directly(self):
        """
        Treasury seed capital is not a direct MentorReward source —
        mentor payouts must come from institutional or user-revenue channels.
        """
        assert not funded(Flow.MentorReward, Source.TreasurySeed)

    @pytest.mark.integration
    def test_sponsor_cannot_fund_mentor_reward(self):
        """Sponsors fund engagement (play/learn) not direct mentorship payouts."""
        assert not funded(Flow.MentorReward, Source.Sponsor)

    @pytest.mark.integration
    def test_circular_economy_is_blocked(self):
        """
        A circular economy where Flow outputs re-enter as Sources without
        new external value is prevented by the no_self_minting axiom.
        """
        # Simulate a circular payout: no external source, non-zero amount
        circular_payout = 50
        circular_source = None  # No external fiat entry
        assert not no_self_minting(Flow.LearnToEarn, circular_payout, circular_source)

    @pytest.mark.integration
    def test_fiat_entry_breaks_circular_dependency(self):
        """
        Introducing any real source resolves the circular dependency.
        """
        circular_payout = 50
        real_source = Source.UserRevenue
        assert no_self_minting(Flow.LearnToEarn, circular_payout, real_source)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])
