class StartupEventMixin:

    async def on_startup(self) -> None:
        pass


class ShutdownEventMixin:

    async def on_shutdown(self) -> None:
        pass
