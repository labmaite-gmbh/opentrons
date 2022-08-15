"""Top-level control interfaces for the Python Protocol API."""

from __future__ import annotations

import logging

from ._core import AbstractProtocolCore
from .labware import Labware

_log = logging.getLogger(__name__)


class ProtocolContext:
    """The primary provider of the Opentrons Python Protocol API.

    A `ProtocolContext` will be created and passed to your protocol's `run` method
    when your protocol is analyzed or run.

    .. versionadded:: 2.0
    """

    def __init__(self, core: AbstractProtocolCore) -> None:
        self._core = core

    def load_labware(self, load_name: str, location: str) -> Labware:
        """Place a labware type into a given location on the deck.

        Args:
            load_name: The unique load name of the labware.
            location: The deck slot to place the labware in, such as "1".

        Returns:
            A labware object for use later in the protocol.
        """
        labware_core = self._core.load_labware(load_name, location)
        return Labware(core=labware_core)
