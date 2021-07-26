import asyncio
import json
from typing import List, Callable, Any, Type
from pydantic import ValidationError

from aio_pika import Queue, Exchange, IncomingMessage
from qlibd.connection_managers.rabbit_connection_manager import RabbitConnectionManager
from qlibd.core.exceptions import MQHandlerException
from qlibd.logger import Logger
from qlibd.serializers.messages import ResponseSerializer
from qlibd.core.base_handler import BaseRequestHandler
from qlibd.core.settings import Settings
from qlibd.helpers.class_helper import ClassHelper

from qlibd.metrics.metric_container import COUNT_ERROR_MESSAGES, COUNT_SUCCESS_MESSAGES, DURATION_WORK


class QueueManager:
	"""
	Infrastructure mq manager for consume messages
	"""

	def __init__(self, settings: Settings, connection_manager: RabbitConnectionManager, logger: Logger) -> None:
		self.settings = settings
		self.connection_manager = connection_manager
		self.logger = logger
		self.handlers: List[BaseRequestHandler] = []

	def add_handler(self, item: BaseRequestHandler):
		self.handlers.append(item)

	async def run_handlers_async(self) -> None:
		"""
		Initialize and start handlers
		@return:
		"""
		for handler in self.handlers:
			await self._create_consumer(handler)

	def _get_data_identifiers(self, data: dict) -> tuple:
		"""
		Gives unique request data

		:param data: request data dict
		:return: Id requested service and id request
		"""
		request_id = data.get('request_id', None)
		if not request_id:
			self.logger.info('Invalid request message. Missing request_id.')

		x_creator_id = data.get('x_creator_id', None)
		if not x_creator_id:
			self.logger.info('Invalid request message. Missing x_creator_id.')

		return request_id, x_creator_id

	async def _send_error_to_result_queues(
			self,
			request_id: str,
			x_creator_id: str,
			error_message: str,
			result_queues: List[str]
	) -> None:
		"""
		Send error to result queues
		@param request_id: Request id
		@param x_creator_id:
		@param error_message: Error message
		@param result_queues: List of queues
		@return: None
		"""
		COUNT_ERROR_MESSAGES.inc()
		response = ResponseSerializer(
			is_success=False,
			request_id=request_id,
			x_creator_id=x_creator_id,
			error_message=error_message
		)
		await self.send_response_to_result_queues(response, result_queues)

	def make_consumer_function(self, request_handler: BaseRequestHandler) -> None:
		"""
		Make dynamic consumer function
		@param request_handler: Request handler class
		@return: Coroutine function for handle message from mq
		"""

		async def _function(message: IncomingMessage) -> None:
			with DURATION_WORK.time():
				async with message.process():
					message_content = message.body.decode('utf-8')
					try:
						data = json.loads(message_content)
					except Exception as ex:
						self.logger.error(f'Unable to parse message. Description: "{ex}"')
						COUNT_ERROR_MESSAGES.inc()
						return

					request_id, x_creator_id = self._get_data_identifiers(data)
					if not (request_id or x_creator_id):
						self.logger.error(f'Error parse message. {message_content}')
						return

					result_queues = request_handler.get_result_queues(x_creator_id)

					class_name = ClassHelper.get_full_class_name(request_handler)
					self.logger.access(class_name, request_handler.get_source_queue(), x_creator_id)

					try:
						request = request_handler.serializer(**data)
					except ValidationError as ex:
						error_message = f'Request body content error. {ex.errors()}'
						await self._send_error_to_result_queues(request_id, x_creator_id, error_message, result_queues)
						return
					except Exception as ex:
						self.logger.error(f'Error parse request from {x_creator_id}. {ex}')
						return

					try:
						result = await request_handler.run_request_handler_async(request)
						if result:
							response = ResponseSerializer(
								is_success=True,
								request_id=request_id,
								x_creator_id=x_creator_id,
								body=result
							)
							await self.send_response_to_result_queues(response, result_queues)
							COUNT_SUCCESS_MESSAGES.inc()
					except MQHandlerException as ex:
						error_message = f'Handler error. {ex}'
						await self._send_error_to_result_queues(request_id, x_creator_id, error_message, result_queues)

		return _function

	async def _create_consumer(self, item: BaseRequestHandler) -> None:
		"""
		Create concrete consumer
		@param item: BaseRequestHandler object
		@return: None
		"""
		self.logger.info(f'Start request handler (consumer) "{item.__class__.__name__}"')

		await self._create_queue_listener(
			queue_name=item.get_source_queue(),
			consumer=self.make_consumer_function(item)
		)

	async def _get_exchange(self, exchange_type: Any) -> Exchange:
		if not self._exchange:
			connection = await self.connection_manager.get_connection_async()
			channel = await connection.channel()
			self._exchange = await channel.declare_exchange(exchange_type, auto_delete=False, durable=True)
		return self._exchange

	async def _create_queue_listener(self, queue_name: str, consumer: Callable, exchange_name: str = "direct") -> Queue:
		"""
		Add listener to queue

		:param queue_name: Name of queue
		:param consumer: Callback function to listen queue
		:param exchange_name: Rabbitmq exchange name
		:return: Returns the queue to listen on
		"""
		connection = await self.connection_manager.get_connection_async()
		channel = await connection.channel(publisher_confirms=True)
		exchange = await channel.declare_exchange(exchange_name, auto_delete=False, durable=True)
		queue = await channel.declare_queue(queue_name, auto_delete=False, durable=True)

		await queue.bind(exchange, queue_name)
		await queue.consume(consumer)

		return queue

	async def send_response_to_result_queues(self, response: ResponseSerializer, queues: List[str]) -> None:
		"""
		Send dict-result to queue list
		"""
		tasks = [
			self.connection_manager.send_data_by_queue_async(response.dict(), queue_name) for queue_name in queues
		]
		await asyncio.gather(*tasks)
