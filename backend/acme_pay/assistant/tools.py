"""The only things the model can do: aggregate-only queries over tested insight services.

Each tool validates its arguments with Pydantic and returns plain JSON. None of them can
return an individual employee (enforced by an integration test over real seeded data).
"""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from acme_pay.assistant.llm import ToolSpec
from acme_pay.insights.service import InsightsService


class NoArguments(BaseModel):
    """Tools that take no input."""

    model_config = ConfigDict(extra="forbid")


class RoleArguments(BaseModel):
    """A job title, exactly as listed by available_filters."""

    model_config = ConfigDict(extra="forbid")

    job_title: str = Field(min_length=1)


class DistributionArguments(BaseModel):
    """Optional filters for a salary histogram."""

    model_config = ConfigDict(extra="forbid")

    country: str | None = Field(default=None, pattern=r"^[A-Za-z]{2}$")
    department: str | None = None
    job_title: str | None = None


@dataclass(frozen=True, slots=True)
class Tool:
    """A callable capability offered to the model."""

    spec: ToolSpec
    arguments: type[BaseModel]
    run: Callable[[InsightsService, Any], Awaitable[BaseModel]]

    async def execute(self, insights: InsightsService, raw: dict[str, Any]) -> dict[str, Any]:
        """Validate ``raw`` arguments, run the tool and return JSON-ready data.

        Raises:
            pydantic.ValidationError: If the arguments are invalid.
        """
        arguments = self.arguments.model_validate(raw)
        result = await self.run(insights, arguments)
        return result.model_dump(mode="json")


def _string(description: str) -> dict[str, str]:
    return {"type": "string", "description": description}


async def _summary(insights: InsightsService, _: NoArguments) -> BaseModel:
    return await insights.pulse()


async def _role(insights: InsightsService, args: RoleArguments) -> BaseModel:
    return await insights.benchmarks(args.job_title)


async def _distribution(insights: InsightsService, args: DistributionArguments) -> BaseModel:
    country = args.country.upper() if args.country else None
    return await insights.distribution(
        country=country, department=args.department, job_title=args.job_title
    )


async def _filters(insights: InsightsService, _: NoArguments) -> BaseModel:
    return await insights.options()


_TOOLS = [
    Tool(
        ToolSpec(
            "org_pay_summary",
            "Organization-wide pay for active employees: headcount, payroll and median salary "
            "in USD, counts below/above the pay band (compa-ratio 0.80-1.20 vs. the median for "
            "the same job title and country), breakdowns by country and department, and the "
            "peer groups with the most people below band.",
            {"type": "object", "properties": {}},
        ),
        NoArguments,
        _summary,
    ),
    Tool(
        ToolSpec(
            "role_pay_by_country",
            "Pay for one job title in every country: headcount, min, 25th percentile, median, "
            "75th percentile, max and average in local currency, plus p25/median/p75 in USD.",
            {
                "type": "object",
                "properties": {"job_title": _string("Exact job title from available_filters.")},
                "required": ["job_title"],
            },
        ),
        RoleArguments,
        _role,
    ),
    Tool(
        ToolSpec(
            "salary_distribution",
            "Histogram of active salaries in 12 equal-width buckets, optionally filtered. "
            "In local currency when a country is given, otherwise in USD.",
            {
                "type": "object",
                "properties": {
                    "country": _string("ISO 3166 alpha-2 code, e.g. DE."),
                    "department": _string("Exact department from available_filters."),
                    "job_title": _string("Exact job title from available_filters."),
                },
            },
        ),
        DistributionArguments,
        _distribution,
    ),
    Tool(
        ToolSpec(
            "available_filters",
            "The countries (code, name, currency), departments and job titles that exist. "
            "Use it to map the user's wording to exact values before calling other tools.",
            {"type": "object", "properties": {}},
        ),
        NoArguments,
        _filters,
    ),
]

TOOLS: dict[str, Tool] = {tool.spec.name: tool for tool in _TOOLS}
