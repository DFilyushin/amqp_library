from qlibd.core.settings import Settings


class BookService:

	def __init__(self, settings: Settings) -> None:
		self.settings = settings

	async def get_book_by_id(self, book_id: int):
		pass
