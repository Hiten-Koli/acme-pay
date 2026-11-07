"""Conversion to the USD reporting currency using dated FX rates."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from acme_pay.domain.money import CurrencyMismatchError, Money, require_currency_code

REPORTING_CURRENCY = "USD"


@dataclass(frozen=True, slots=True)
class FxRate:
    """How many US dollars one unit of ``currency`` was worth on ``effective_date``.

    Raises:
        ValueError: If the currency code is malformed or the rate is not positive.
    """

    currency: str
    rate_to_usd: Decimal
    effective_date: date

    def __post_init__(self) -> None:
        require_currency_code(self.currency)
        if self.rate_to_usd <= 0:
            raise ValueError(f"FX rate must be positive, got {self.rate_to_usd}")


@dataclass(frozen=True, slots=True)
class ConvertedMoney:
    """A USD amount together with the date of the rate that produced it."""

    money: Money
    rate_date: date


def to_usd(money: Money, rate: FxRate) -> ConvertedMoney:
    """Convert ``money`` to USD exactly; round only when storing or displaying.

    Raises:
        CurrencyMismatchError: If ``rate`` is for a different currency than ``money``.
    """
    if rate.currency != money.currency:
        raise CurrencyMismatchError(f"Rate is for {rate.currency}, money is in {money.currency}")
    usd = Money(money.amount * rate.rate_to_usd, REPORTING_CURRENCY)
    return ConvertedMoney(money=usd, rate_date=rate.effective_date)
