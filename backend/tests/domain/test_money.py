from decimal import Decimal

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from acme_pay.domain.money import CurrencyMismatchError, Money

# Realistic annual salaries: up to 12 integer digits, exactly 2 decimal places.
amounts = st.decimals(min_value=0, max_value=Decimal("999999999999.99"), places=2)
currencies = st.sampled_from(["USD", "EUR", "GBP", "INR", "JPY", "BRL"])


class TestConstruction:
    def test_holds_amount_and_currency(self) -> None:
        money = Money(Decimal("85000.50"), "EUR")

        assert money.amount == Decimal("85000.50")
        assert money.currency == "EUR"

    @pytest.mark.parametrize("code", ["eur", "EURO", "E1R", ""])
    def test_rejects_currency_codes_that_are_not_iso_4217_shaped(self, code: str) -> None:
        with pytest.raises(ValueError, match="ISO 4217"):
            Money(Decimal(1), code)

    def test_rejects_float_amounts_because_they_are_inexact(self) -> None:
        with pytest.raises(TypeError, match="Decimal"):
            Money(0.1, "USD")  # type: ignore[arg-type]

    @pytest.mark.parametrize("amount", ["NaN", "Infinity"])
    def test_rejects_non_finite_amounts(self, amount: str) -> None:
        with pytest.raises(ValueError, match="finite"):
            Money(Decimal(amount), "USD")

    def test_is_immutable(self) -> None:
        money = Money(Decimal(1), "USD")

        with pytest.raises(AttributeError):
            money.amount = Decimal(2)  # type: ignore[misc]


class TestArithmetic:
    def test_adds_amounts_of_the_same_currency(self) -> None:
        total = Money(Decimal("0.10"), "USD") + Money(Decimal("0.20"), "USD")

        assert total == Money(Decimal("0.30"), "USD")

    def test_subtracts_amounts_of_the_same_currency(self) -> None:
        difference = Money(Decimal("100.00"), "INR") - Money(Decimal("40.25"), "INR")

        assert difference == Money(Decimal("59.75"), "INR")

    def test_refuses_to_mix_currencies(self) -> None:
        with pytest.raises(CurrencyMismatchError):
            _ = Money(Decimal(1), "USD") + Money(Decimal(1), "EUR")

    @given(a=amounts, b=amounts, currency=currencies)
    def test_addition_is_exact(self, a: Decimal, b: Decimal, currency: str) -> None:
        assert (Money(a, currency) + Money(b, currency)).amount == a + b

    @given(a=amounts, b=amounts, currency=currencies)
    def test_subtraction_undoes_addition(self, a: Decimal, b: Decimal, currency: str) -> None:
        assert Money(a, currency) + Money(b, currency) - Money(b, currency) == Money(a, currency)

    @given(a=amounts, b=amounts, first=currencies, second=currencies)
    def test_different_currencies_never_combine(
        self, a: Decimal, b: Decimal, first: str, second: str
    ) -> None:
        assume(first != second)
        with pytest.raises(CurrencyMismatchError):
            _ = Money(a, first) + Money(b, second)


class TestRounding:
    @pytest.mark.parametrize(
        ("amount", "expected"),
        [
            ("10.005", "10.00"),  # half to even: rounds down to the even cent
            ("10.015", "10.02"),  # half to even: rounds up to the even cent
            ("10.0149", "10.01"),
        ],
    )
    def test_rounds_to_cents_using_bankers_rounding(self, amount: str, expected: str) -> None:
        assert Money(Decimal(amount), "USD").rounded() == Money(Decimal(expected), "USD")
