from abc import ABC, abstractmethod
from typing import Any


class NodeAdapter(ABC):

    @abstractmethod
    async def execute(
        self,
        config: dict[str, Any],
        input_data: dict[str, Any],
    ) -> dict[str, Any]:
        pass