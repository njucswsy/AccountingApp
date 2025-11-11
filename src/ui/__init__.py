"""User interface components.

This package contains implementations of user interfaces for
the accounting application. The command line interface is the
primary UI for this demonstration, but the modular structure
allows for alternative UIs (e.g. graphical, web) to be added
in the future without altering the underlying models or
services.
"""

from .cli import CommandLineUI  # noqa: F401