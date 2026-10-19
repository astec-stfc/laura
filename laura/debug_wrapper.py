"""
LAURA logging utilities.

The library uses the standard Python :mod:`logging` module under a single
``"laura"`` logger hierarchy so that calling code can control verbosity
without touching library internals::

    import logging
    logging.getLogger("laura").setLevel(logging.DEBUG)

Or use the convenience helper provided here::

    from laura import set_log_level
    set_log_level("DEBUG")          # show all loader / model diagnostics
    set_log_level("WARNING")        # quiet mode (default)

Sub-loggers
-----------
``laura``
    Root logger for the whole library.
``laura.loader``
    Emits one DEBUG line per successfully parsed element, WARNING when an
    element is skipped (unknown hardware_type), and ERROR for Pydantic
    validation failures.
``laura.model``
    Model construction events (layout / section building, etc.).
"""

import logging

# ── Library-wide logger (no handlers attached — callers configure these) ──────
_logger = logging.getLogger("laura")


def set_log_level(level: int | str) -> None:
    """Set the verbosity of all LAURA loggers.

    Parameters
    ----------
    level:
        Either a :mod:`logging` integer constant (e.g. ``logging.DEBUG``)
        or its string name (``"DEBUG"``, ``"INFO"``, ``"WARNING"`` …).

    Examples
    --------
    >>> from laura import set_log_level
    >>> set_log_level("DEBUG")
    """
    if isinstance(level, str):
        level = logging.getLevelName(level.upper())
    _logger.setLevel(level)
    # Ensure there is at least one handler so messages are visible
    if not _logger.handlers:
        _add_default_handler()


def _add_default_handler() -> None:
    """Attach a stderr StreamHandler with a readable format if none exist."""
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s  %(levelname)-8s  %(name)s — %(message)s", datefmt="%H:%M:%S"
        )
    )
    _logger.addHandler(handler)
