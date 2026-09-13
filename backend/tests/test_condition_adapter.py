import pytest

from app.adapters.condition import ConditionAdapter


@pytest.mark.asyncio
async def test_condition_greater_than():
    adapter = ConditionAdapter()

    result = await adapter.execute(
        {
            "field": "amount",
            "operator": "greater_than",
            "value": 1000,
        },
        {
            "amount": 1500,
        },
    )

    assert result["result"] is True