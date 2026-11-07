from decimal import Decimal

import pytest
from hypothesis import given
from hypothesis import strategies as st

from acme_pay.domain.compa_ratio import compa_ratio
from acme_pay.domain.money import CurrencyMismatchError, Money

salaries = st.decimals(min_value=Decimal("0.01"), max_value=Decimal("99999999.99"), places=2)


def eur(amount: str | Decimal) -> Money:
    return Money(Decimal(amount), "EUR")


def test_is_salary_divided_by_peer_median_to_two_decimals() -> None:
    assert compa_ratio(eur("90000"), peer_median=eur("100000")) == Decimal("0.90")


def test_rounds_half_even() -> None:
    assert compa_ratio(eur("100125"), peer_median=eur("100000")) == Decimal("1.00")


def test_refuses_to_compare_different_currencies() -> None:
    with pytest.raises(CurrencyMismatchError):
        compa_ratio(eur("1"), peer_median=Money(Decimal(1), "USD"))


@pytest.mark.parametrize("median", ["0", "-1"])
def test_rejects_a_non_positive_peer_median(median: str) -> None:
    with pytest.raises(ValueError, match="positive"):
        compa_ratio(eur("1"), peer_median=eur(median))


@given(salary=salaries)
def test_someone_paid_exactly_the_median_has_a_ratio_of_one(salary: Decimal) -> None:
    assert compa_ratio(eur(salary), peer_median=eur(salary)) == Decimal("1.00")


@given(lower=salaries, raise_by=salaries, median=salaries)
def test_a_higher_salary_never_gets_a_lower_ratio(
    lower: Decimal, raise_by: Decimal, median: Decimal
) -> None:
    before = compa_ratio(eur(lower), peer_median=eur(median))
    after = compa_ratio(eur(lower + raise_by), peer_median=eur(median))

    assert after >= before
