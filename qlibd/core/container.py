import asyncio
from abc import ABC

from qlibd.core.event_mixins import StartupEventMixin, ShutdownEventMixin
from injector import Injector, Module


class BaseContainer(ABC, Module):
    pass


class ContainerManager:

    def __init__(self, container_cls: BaseContainer) -> None:
        self.container = Injector(container_cls())

    def get_container(self) -> Injector:
        return self.container

    async def run_startup(self) -> None:
        tasks = []

        for binding in self.container.binder._bindings:
            if issubclass(binding, StartupEventMixin):
                startup_container_obj = self.container.get(binding)
                tasks.append(startup_container_obj.on_startup())

        await asyncio.gather(*tasks)

    async def run_shutdown(self) -> None:
        tasks = []

        for binding in self.container.binder._bindings:
            if issubclass(binding, ShutdownEventMixin):
                startup_container_obj = self.container.get(binding)
                tasks.append(startup_container_obj.on_shutdown())

        await asyncio.gather(*tasks)
