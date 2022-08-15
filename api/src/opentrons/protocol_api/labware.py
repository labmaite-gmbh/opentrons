"""Labware control interfaces for the Python Protocol API."""
from __future__ import annotations

import logging

from ._core import AbstractLabwareCore
from .labware_old import Well, load, load_from_definition

_log = logging.getLogger(__name__)


class Labware:
    """An interface representing a piece of labware on the deck.

    A "labware" is a tip rack, well plate, tube rack, etc.
    You can create a `Labware` using ``ProtocolContext.load_labware()``.
    """

    def __init__(self, core: AbstractLabwareCore) -> None:
        self._core = core

    @property
    def load_name(self) -> str:
        return self._core.load_name
