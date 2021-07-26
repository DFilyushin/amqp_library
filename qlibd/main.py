import typer
import env_file as env_file_loader

from qlibd.containers.application_container import ApplicationContainer
from qlibd.core.application import Application


def main(env_file: str = None):
    try:
        if env_file:
            env_file_loader.load(env_file)
    except OSError:
        typer.echo("Env file not exists!")
        return

    application = Application(ApplicationContainer)
    application.run()


if __name__ == "__main__":
    typer.run(main)
