"""The Gemini adapter speaks the generateContent wire format (checked with a mock transport)."""

import json
from typing import Any

import httpx
import pytest

from acme_pay.assistant.gemini import GeminiProvider
from acme_pay.assistant.llm import LLMUnavailableError, ToolResult, ToolSpec

pytestmark = pytest.mark.anyio

TOOL = ToolSpec(
    name="role_pay_by_country",
    description="Pay for one job title in each country.",
    parameters={"type": "object", "properties": {"job_title": {"type": "string"}}},
)
FUNCTION_CALL_CONTENT = {
    "role": "model",
    "parts": [
        {
            "functionCall": {
                "id": "fc-1",
                "name": "role_pay_by_country",
                "args": {"job_title": "Data Scientist"},
            },
            "thoughtSignature": "sig-A",
        }
    ],
}


def gemini_reply(content: dict[str, Any]) -> httpx.Response:
    return httpx.Response(200, json={"candidates": [{"content": content}]})


def provider_with(responses: list[httpx.Response], sent: list[dict[str, Any]]) -> GeminiProvider:
    def handle(request: httpx.Request) -> httpx.Response:
        assert request.headers["x-goog-api-key"] == "test-key"
        assert request.url.path.endswith("/models/gemini-test:generateContent")
        sent.append(json.loads(request.content))
        return responses.pop(0)

    client = httpx.AsyncClient(transport=httpx.MockTransport(handle))
    return GeminiProvider(api_key="test-key", model="gemini-test", client=client)


async def test_parses_function_calls_and_sends_system_instruction_and_tools() -> None:
    sent: list[dict[str, Any]] = []
    provider = provider_with([gemini_reply(FUNCTION_CALL_CONTENT)], sent)

    reply = await provider.start(system="Be exact.", tools=[TOOL]).send("Where are DS paid most?")

    [call] = reply.calls
    assert (call.id, call.name, call.arguments) == (
        "fc-1",
        "role_pay_by_country",
        {"job_title": "Data Scientist"},
    )
    body = sent[0]
    assert body["systemInstruction"]["parts"][0]["text"] == "Be exact."
    assert body["tools"][0]["functionDeclarations"][0]["name"] == "role_pay_by_country"
    assert body["contents"] == [{"role": "user", "parts": [{"text": "Where are DS paid most?"}]}]


async def test_echoes_model_turns_verbatim_and_answers_calls_by_id() -> None:
    sent: list[dict[str, Any]] = []
    final = gemini_reply({"role": "model", "parts": [{"text": "The US pays most."}]})
    provider = provider_with([gemini_reply(FUNCTION_CALL_CONTENT), final], sent)
    conversation = provider.start(system="s", tools=[TOOL])

    call = (await conversation.send("q")).calls[0]
    reply = await conversation.send_results([ToolResult(call=call, content={"countries": []})])

    assert reply.text == "The US pays most."
    contents = sent[1]["contents"]
    assert contents[1] == FUNCTION_CALL_CONTENT  # thought signature preserved exactly
    assert contents[2] == {
        "role": "user",
        "parts": [
            {
                "functionResponse": {
                    "id": "fc-1",
                    "name": "role_pay_by_country",
                    "response": {"countries": []},
                }
            }
        ],
    }


@pytest.mark.parametrize("status", [429, 500, 503])
async def test_provider_errors_become_a_single_unavailable_error(status: int) -> None:
    provider = provider_with([httpx.Response(status, json={"error": {}})], [])

    with pytest.raises(LLMUnavailableError):
        await provider.start(system="s", tools=[TOOL]).send("q")
