"""Entry point for the accounting application.

Running this module directly will launch the command line
interface. This file is intentionally kept small to focus on
initialisation and delegation to the UI class. This separation
allows the application to be embedded in different contexts
without modification; for example, the CLI could be replaced
with a graphical interface simply by importing and invoking
another UI class from here.
"""

from src.ui.cli import CommandLineUI


def main() -> None:
    """Instantiate the command line UI and begin interaction."""
    ui = CommandLineUI()
    ui.run()


if __name__ == "__main__":
    main()
