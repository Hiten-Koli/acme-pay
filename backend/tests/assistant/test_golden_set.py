"""The golden eval set must stay consistent with the real tools (checked in CI, no model)."""

import pytest

from acme_pay.assistant.evals import GOLDEN, GoldenCase, matches
from acme_pay.assistant.llm import ToolCall
from acme_pay.assistant.tools import TOOLS


@pytest.mark.parametrize("case", GOLDEN, ids=lambda case: case.question)
def test_every_golden_case_names_a_real_tool_with_valid_arguments(case: GoldenCase) -> None:
    tool = TOOLS[case.tool]

    tool.arguments.model_validate(case.arguments)


def test_every_tool_is_covered_by_at_least_one_golden_question() -> None:
    covered = {case.tool for case in GOLDEN}

    assert covered >= set(TOOLS) - {"available_filters"}


def test_matching_ignores_case_and_extra_arguments() -> None:
    case = GoldenCase("q", "salary_distribution", {"country": "IN"})

    assert matches(case, ToolCall("1", "salary_distribution", {"country": "in", "job_title": "X"}))
    assert not matches(case, ToolCall("1", "salary_distribution", {"country": "DE"}))
    assert not matches(case, ToolCall("1", "org_pay_summary", {}))
