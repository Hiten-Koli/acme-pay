"""Compa-ratio: how an individual's pay compares with their peer group."""

from decimal import ROUND_HALF_EVEN, Decimal
from enum import StrEnum

from acme_pay.domain.money import CurrencyMismatchError, Money

RATIO_PRECISION = Decimal("0.01")
# Standard compensation-practice band: within 20% of the peer median.
BAND_LOW = Decimal("0.80")
BAND_HIGH = Decimal("1.20")


class BandPosition(StrEnum):
    """Where a compa-ratio falls relative to the pay band."""

    BELOW = "below"
    WITHIN = "within"
    ABOVE = "above"


def compa_ratio(salary: Money, *, peer_median: Money) -> Decimal:
    """Return ``salary / peer_median`` to two decimals (1.00 means paid at the median).

    Args:
        salary: The individual's salary.
        peer_median: Median salary of the peer group (same role, same country).

    Raises:
        CurrencyMismatchError: If the two amounts are in different currencies.
        ValueError: If the peer median is not positive.
    """
    if salary.currency != peer_median.currency:
        raise CurrencyMismatchError(
            f"Cannot compare {salary.currency} salary with {peer_median.currency} median"
        )
    if peer_median.amount <= 0:
        raise ValueError(f"Peer median must be positive, got {peer_median.amount}")
    return (salary.amount / peer_median.amount).quantize(RATIO_PRECISION, rounding=ROUND_HALF_EVEN)


def band_position(ratio: Decimal) -> BandPosition:
    """Classify a compa-ratio against the 0.80-1.20 band (boundaries are within)."""
    if ratio < BAND_LOW:
        return BandPosition.BELOW
    if ratio > BAND_HIGH:
        return BandPosition.ABOVE
    return BandPosition.WITHIN
