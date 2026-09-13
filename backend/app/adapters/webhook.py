from typing import Any

from app.adapters.base import NodeAdapter


class WebhookAdapter(NodeAdapter):

    async def execute(
        self,
        config: dict[str, Any],
        input_data: dict[str, Any],
    ) -> dict[str, Any]:
        return input_data