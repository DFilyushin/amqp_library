import traceback
import asyncio
from injector import Module
from uvicorn import Server, Config

from qlibd.core.container import ContainerManager
from qlibd.core.queue_manager import QueueManager
from qlibd.core.settings import Settings
from qlibd.logger.logger import Logger
from qlibd.http_server.http_server import HttpServerApplication
from qlibd.handlers.book_handler import BookHandler


class Application:
	def __init__(self, container_cls: Module, env_file: str = '.env') -> None:
		self.container_manager = ContainerManager(container_cls)
		self.container = self.container_manager.get_container()
		self.loop = asyncio.get_event_loop()
		self.logger = self.container.get(Logger)
		self.settings = self.container.get(Settings)
		self.__setup_application(env_file)

	def __setup_application(self, env_file: str):
		try:
			self.queue_manager = self._get_queue_manager()
			self.http_server = self.__get_http_server()
		except Exception as exception:
			self.logger.error(traceback.format_exc())
			raise exception

	def __get_queue_manager(self) -> QueueManager:
		queue_manager = self.container.get(QueueManager)
		book_handler = self.container.get(BookHandler)
		queue_manager.add_handler(book_handler)
		return queue_manager

	def __get_http_server(self) -> Server:
		server_application = HttpServerApplication(self.settings)
		config = Config(
			app=server_application,
			loop=self.loop,
			host=self.settings.http_host,
			port=self.settings.http_port,
			log_config=server_application.get_config_log(),
			access_log=False
		)
		return Server(config)

	def run(self) -> None:
		"""
		Main run function
		:return:
		"""
		name_application = self.settings.application_name
		try:
			self.logger.info(f'Run {name_application} application')
			self.loop.run_until_complete(self.container_manager.run_startup())
			self.loop.run_until_complete(self._add_mongo_indexes())

			tasks = asyncio.gather(
				self.queue_manager.run_handlers_async(),
				self.http_server.serve()
			)

			self.loop.run_until_complete(tasks)
			self.loop.run_forever()
		except KeyboardInterrupt:
			pass
		except Exception as exception:
			self.logger.error(traceback.format_exc())
			raise exception
		finally:
			self.loop.run_until_complete(self.container_manager.run_shutdown())
			self.loop.close()
			self.logger.info(f'Stop application {name_application}...')
