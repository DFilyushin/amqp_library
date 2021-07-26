from fastapi import FastAPI
from uvicorn.config import LOGGING_CONFIG

from qlibd.http_server.routes import router
from qlibd.core.settings import Settings


class HttpServerApplication(FastAPI):

    def __init__(self, settings: Settings) -> None:
        super(HttpServerApplication, self).__init__(title=settings.application_name)
        self._include_routes()

    def _include_routes(self) -> None:
        self.include_router(router, tags=['Maintain application'])

    @staticmethod
    def get_config_log() -> dict:
        config_log = LOGGING_CONFIG

        config_log["formatters"] = {
            "default": {
                "()": "fintech_logger_core.formatters.colored_formatter.ColoredFormatter",
                "fmt": "%(levelprefix)s %(message)s"
            },
            "access": {
                "()": "ris.http_server.logger.ServerLoggerFormatter",
                "fmt": '%(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',
                'use_colors': True
            },
        }
        return config_log
