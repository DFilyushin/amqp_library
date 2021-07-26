from injector import singleton, provider, Module
from qlibd.core.settings import Settings
from qlibd.logger.logger import Logger
from qlibd.services.book_service import BookService


class ApplicationContainer(Module):

	@singleton
	@provider
	def provide_settings(self) -> Settings:
		return Settings()

	@singleton
	@provider
	def provide_logger(self, settings: Settings) -> Logger:
		return Logger(settings.logger_level)

	@singleton
	@provider
	def provide_service(self, settings: Settings) -> BookService:
		return BookService(settings)
