import pytest

from app.adapters.llm import LLMAdapter
from app.adapters.webhook import WebhookAdapter


@pytest.mark.asyncio
async def test_webhook_adapter():
    data = {"message": "hello"}

    result = await WebhookAdapter().execute({}, data)

    assert result == data


@pytest.mark.asyncio
async def test_llm_adapter():
    result = await LLMAdapter().execute(
        {"prompt": "Summarize"},
        {"message": "hello"},
    )

    assert result["prompt"] == "Summarize"
    assert "Mock LLM response" in result["text"]