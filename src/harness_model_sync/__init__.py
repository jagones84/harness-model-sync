"""harness-model-sync: one source of truth for model context windows, rendered per harness."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("harness-model-sync")
except PackageNotFoundError:
    __version__ = "0.2.0"
