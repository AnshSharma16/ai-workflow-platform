from typing import Any

from app.adapters.base import NodeAdapter


class LLMAdapter(NodeAdapter):

    async def execute(
        self,
        config: dict[str, Any],
        input_data: dict[str, Any],
    ) -> dict[str, Any]:

        prompt = config.get(
            "prompt",
            "Process the input.",
        )

        return {
            "text": f"Mock LLM response for: {input_data}",
            "prompt": prompt,
        }