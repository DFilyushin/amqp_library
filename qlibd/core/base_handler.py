from abc import ABC, abstractmethod
from typing import Type, List, Optional

from qlibd.serializers.messages import BaseSerializer


class BaseRequestHandler(ABC):
    def __init__(self, serializer: Type[BaseSerializer]):
        self.serializer = serializer

    def get_serializer(self) -> Type[BaseSerializer]:
        return self.serializer

    @abstractmethod
    def get_source_queue(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_result_queues(self, x_creator_id: str) -> List[str]:
        raise NotImplementedError

    @abstractmethod
    async def run_request_handler_async(self, request: Type[BaseSerializer]) -> Optional[dict]:
        raise NotImplementedError
