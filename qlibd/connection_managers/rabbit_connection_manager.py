import asyncio
import json
from asyncio import Queue
from typing import Callable
from accessify import implements

from aio_pika import Exchange, connect_robust, Message, Channel
from aio_pika.connection import Connection
from qlibd.connection_managers.interfaces.connection_manager_interface import ConnectionManagerInterface
from qlibd.core.event_mixins import StartupEventMixin, ShutdownEventMixin
from qlibd.core.settings import Settings


@implements(ConnectionManagerInterface)
class RabbitConnectionManager(StartupEventMixin, ShutdownEventMixin):
    def __init__(self, settings: Settings) -> None:
        self.rabbit_uri = settings.rabbit_queue_dsn
        self.prefetch_count = settings.rabbitmq_prefetch_count
        self.exchange_type = settings.rabbitmq_exchange_type
        self._connection = None
        self._channel = None
        self._exchange = None

    async def run_startup(self) -> None:
        self._connection = await connect_robust(self.rabbit_uri, loop=asyncio.get_running_loop())

    async def run_shutdown(self) -> None:
        if self._connection:
            await self._connection.close()

    async def get_connection_async(self) -> Connection:
        """
        Get connection
        :return: Connection
        """
        return self._connection

    async def get_channel_async(self) -> Channel:
        if not self._channel:
            connection = await self.get_connection_async()
            self._channel = await connection.channel()
            await self._channel.set_qos(prefetch_count=self.prefetch_count)
        return self._channel

    async def get_exchange_async(self) -> Exchange:
        """
        Get exchange
        :return: Exchange
        """
        if not self._exchange:
            channel = await self.get_channel_async()
            self._exchange = await channel.declare_exchange(self.exchange_type, auto_delete=False, durable=True)
        return self._exchange

    async def create_queue_listener(
            self,
            queue_name: str,
            callback_worker: Callable
    ) -> Queue:
        """
        Add listener to queue
        :param queue_name: Name of queue
        :param callback_worker: Callback function to listen queue
        :return: Returns the queue to listen on
        """
        channel = await self.get_channel_async()
        exchange = await self.get_exchange_async()
        queue = await channel.declare_queue(queue_name, auto_delete=False, durable=True)

        await queue.bind(exchange, queue_name)
        await queue.consume(callback_worker)

        return queue

    async def declare_queue_async(self, queue_name: str, dead_letter_queue_name: str) -> None:
        """
        Creates a queue in rabbitmq
        :param queue_name: Queue name
        :param dead_letter_queue_name: Dead letter queue for reservation
        :return: Exchange
        """
        queue_arguments = {}
        if dead_letter_queue_name:
            queue_arguments = {
                'x-dead-letter-exchange': '',
                'x-dead-letter-routing-key': dead_letter_queue_name
            }
        connection = await self.get_connection_async()
        channel = await connection.channel()
        queue = await channel.declare_queue(queue_name, auto_delete=False, durable=True, arguments=queue_arguments)
        exchange = await self.get_exchange_async()
        await queue.bind(exchange, queue_name)

    async def send_data_by_queue_async(self, data: dict, queue_name: str, dead_letter_queue_name: str) -> None:
        """
        Send data to the queue

        :param data: data to transfer to the queue
        :param queue_name: name of the queue to write data
        :param dead_letter_queue_name: Name of queue to dead messages
        :return: :class:`None` instance
        """
        data_bytes = json.dumps(data).encode()
        exchange = await self.get_exchange_async()
        await self.declare_queue_async(queue_name, dead_letter_queue_name)
        await exchange.publish(Message(data_bytes), routing_key=queue_name)
