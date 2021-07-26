from typing import Optional
import logging
from logging import StreamHandler, Logger as BaseLogger
from qlibd.logger.colored_formatter import ColoredFormatter


class Logger(BaseLogger):
	ACCESS = 25
	SUCCESS_STATUS = 'SUCCESS'
	ERROR_STATUS = 'ERROR'

	def __init__(self, level: int = logging.DEBUG) -> None:
		super().__init__('app.logger', level)
		logging.addLevelName(Logger.ACCESS, 'ACCESS')
		self._setup_handlers()

	def _setup_handlers(self) -> None:
		colored_handler = StreamHandler()
		colored_handler.setFormatter(ColoredFormatter())
		self.handlers = [colored_handler]


def access(
		self,
		method: Optional[str] = None,
		path: Optional[str] = None,
		module: Optional[str] = None,
		status_code: Optional[int] = None,
		status: Optional[str] = Logger.SUCCESS_STATUS,
		client_host: Optional[str] = None,
		creator_id: Optional[str] = None
) -> None:
	if self.isEnabledFor(Logger.ACCESS):
		args = {
			'method': method,
			'path': path,
			'module': module,
			'status_code': status_code,
			'status': status,
			'client_host': client_host,
			'creator_id': creator_id,
		}
		self._log(Logger.ACCESS, None, args)


def error(
		self,
		traceback: str,
		method: Optional[str] = None,
		path: Optional[str] = None,
		module: Optional[str] = None,
		client_host: Optional[str] = None,
		creator_id: Optional[str] = None,
		query_string: Optional[str] = None,
		form_params: Optional[dict] = None,
		body: Optional[str] = None
) -> None:
	if self.isEnabledFor(logging.ERROR):
		args = {
			'traceback': traceback,
			'method': method,
			'path': path,
			'module': module,
			'client_host': client_host,
			'creator_id': creator_id,
			'query_string': query_string,
			'form_params': form_params,
			'body': body,
		}
		self._log(logging.ERROR, traceback, args)
