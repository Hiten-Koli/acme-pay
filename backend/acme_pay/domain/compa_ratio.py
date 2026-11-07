"""Compa-ratio: how an individual's pay compares with their peer group."""

from decimal import ROUND_HALF_EVEN, Decimal

from acme_pay.domain.money import CurrencyMismatchError, Money

RATIO_PRECISION = Decimal("0.01")


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
