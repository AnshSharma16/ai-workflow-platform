from typing import Any

from app.adapters.base import NodeAdapter


class ConditionAdapter(NodeAdapter):

    async def execute(
        self,
        config: dict[str, Any],
        input_data: dict[str, Any],
    ) -> dict[str, Any]:

        field = config["field"]
        operator = config["operator"]
        expected = config["value"]

        actual = input_data.get(field)

        if operator == "equals":
            result = actual == expected

        elif operator == "not_equals":
            result = actual != expected

        elif operator == "greater_than":
            result = actual > expected

        elif operator == "less_than":
            result = actual < expected

        elif operator == "contains":
            result = expected in actual

        else:
            raise ValueError(
                f"Unsupported operator: {operator}"
            )

        return {
            "result": result,
        }