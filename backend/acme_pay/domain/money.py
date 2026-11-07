"""Exact monetary amounts tied to a currency."""

import re
from dataclasses import dataclass
from decimal import ROUND_HALF_EVEN, Decimal
from typing import Self

_CURRENCY_CODE = re.compile(r"[A-Z]{3}")
CENT = Decimal("0.01")


class CurrencyMismatchError(ValueError):
    """Raised when combining money in different currencies without conversion."""


@dataclass(frozen=True, slots=True)
class Money:
    """An exact amount in one currency.

    Attributes:
        amount: Exact decimal amount. Floats are rejected because they cannot
            represent most decimal values exactly.
        currency: ISO 4217 currency code, e.g. ``"EUR"``.

    Raises:
        TypeError: If ``amount`` is not a ``Decimal``.
        ValueError: If ``amount`` is not finite or ``currency`` is malformed.
    """

    amount: Decimal
    currency: str

    def __post_init__(self) -> None:
        if not isinstance(self.amount, Decimal):
            raise TypeError(f"Money amount must be a Decimal, got {type(self.amount).__name__}")
        if not self.amount.is_finite():
            raise ValueError(f"Money amount must be finite, got {self.amount}")
        if not _CURRENCY_CODE.fullmatch(self.currency):
            raise ValueError(f"Currency must be an ISO 4217 code, got {self.currency!r}")

    def __add__(self, other: Self) -> Self:
        self._require_same_currency(other)
        return type(self)(self.amount + other.amount, self.currency)

    def __sub__(self, other: Self) -> Self:
        self._require_same_currency(other)
        return type(self)(self.amount - other.amount, self.currency)

    def rounded(self) -> Self:
        """Return the amount rounded to cents with banker's rounding (half-even)."""
        return type(self)(self.amount.quantize(CENT, rounding=ROUND_HALF_EVEN), self.currency)

    def _require_same_currency(self, other: "Money") -> None:
        if other.currency != self.currency:
            raise CurrencyMismatchError(
                f"Cannot combine {self.currency} with {other.currency}; convert first"
            )
