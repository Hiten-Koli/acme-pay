from datetime import date
from decimal import Decimal

import pytest
from hypothesis import given
from hypothesis import strategies as st

from acme_pay.domain.fx import FxRate, to_usd
from acme_pay.domain.money import CurrencyMismatchError, Money

RATE_DATE = date(2026, 10, 1)
EUR_RATE = FxRate("EUR", Decimal("1.08"), RATE_DATE)

amounts = st.decimals(min_value=0, max_value=Decimal("999999999999.99"), places=2)
rates = st.decimals(min_value=Decimal("0.000001"), max_value=Decimal(1000), places=6)


class TestFxRate:
    @pytest.mark.parametrize("rate", ["0", "-1.5"])
    def test_rejects_non_positive_rates(self, rate: str) -> None:
        with pytest.raises(ValueError, match="positive"):
            FxRate("EUR", Decimal(rate), RATE_DATE)

    def test_rejects_malformed_currency_codes(self) -> None:
        with pytest.raises(ValueError, match="ISO 4217"):
            FxRate("euro", Decimal(1), RATE_DATE)


class TestToUsd:
    def test_converts_using_the_rate(self) -> None:
        converted = to_usd(Money(Decimal("100000.00"), "EUR"), EUR_RATE)

        assert converted.money == Money(Decimal("108000.0000"), "USD")

    def test_carries_the_rate_date_so_figures_are_explainable(self) -> None:
        converted = to_usd(Money(Decimal(1), "EUR"), EUR_RATE)

        assert converted.rate_date == RATE_DATE

    def test_refuses_a_rate_for_a_different_currency(self) -> None:
        with pytest.raises(CurrencyMismatchError):
            to_usd(Money(Decimal(1), "INR"), EUR_RATE)

    @given(a=amounts, b=amounts, rate=rates)
    def test_conversion_is_exact_so_totals_reconcile(
        self, a: Decimal, b: Decimal, rate: Decimal
    ) -> None:
        fx = FxRate("EUR", rate, RATE_DATE)

        converted_total = to_usd(Money(a, "EUR") + Money(b, "EUR"), fx).money
        total_of_converted = to_usd(Money(a, "EUR"), fx).money + to_usd(Money(b, "EUR"), fx).money

        assert converted_total == total_of_converted
