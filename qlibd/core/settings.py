from typing import Optional
from pydantic import BaseSettings
from logging import INFO


class Settings(BaseSettings):
	application_name: str
	logger_level: int = INFO

	http_host: str = '0.0.0.0'
	http_port: int = 80

	mongo_hosts: str
	mongo_username: str
	mongo_password: str
	mongo_db: str
	mongo_replica_set_name: Optional[str] = None
	mongo_auth_db: str

	rabbitmq_host: str
	rabbitmq_port: int
	rabbitmq_username: str
	rabbitmq_password: str
	rabbitmq_vhost: str = ''
	rabbitmq_source_queue_name: str
	rabbitmq_exchange_type: str = 'direct'
	rabbitmq_prefetch_count: int

	@property
	def rabbit_queue_dsn(self) -> str:
		"""
		Get connection string for outer queue
		:return: Connection URI string
		"""
		return 'amqp://{}:{}@{}:{}/{}'.format(
			self.rabbitmq_username,
			self.rabbitmq_password,
			self.rabbitmq_host,
			self.rabbitmq_port,
			self.rabbitmq_vhost
		)

	@property
	def mongodb_dsn(self) -> str:
		"""
		Get connection string for mongodb

		:return: Connection URI string
		"""
		mongodb_dsn = 'mongodb://{}:{}@{}/{}'.format(
			self.mongo_username,
			self.mongo_password,
			self.mongo_hosts,
			self.mongo_auth_db
		)

		if self.mongo_replica_set_name:
			mongodb_dsn += f'?replicaSet={self.mongo_replica_set_name}'

		return mongodb_dsn
