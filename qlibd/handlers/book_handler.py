from typing import Type, Optional, List

from qlibd.core.base_handler import BaseRequestHandler
from qlibd.serializers.messages import BaseSerializer


class BookHandler(BaseRequestHandler):
	def get_source_queue(self) -> str:
		pass

	def get_result_queues(self, x_creator_id: str) -> List[str]:
		pass

	async def run_request_handler_async(self, request: Type[BaseSerializer]) -> Optional[dict]:
		pass
