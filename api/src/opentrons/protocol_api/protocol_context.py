"""Top-level control interfaces for the Python Protocol API."""
from __future__ import annotations

import logging
from typing import Optional

from opentrons.protocols.api_support.types import APIVersion
from opentrons.protocols.api_support.util import requires_version
from opentrons.protocols.api_support.definitions import MAX_SUPPORTED_VERSION

from ._core import AbstractProtocolCore
from .labware import Labware

_log = logging.getLogger(__name__)


class ProtocolContext:
    """The primary provider of the Opentrons Python Protocol API.

    A `ProtocolContext` will be created and passed to your protocol's `run` method
    when your protocol is analyzed or run.

    .. versionadded:: 2.0
    """

    def __init__(
        self,
        core: AbstractProtocolCore,
        api_version: Optional[APIVersion] = None,
    ) -> None:
        self._core = core
        self._api_version = api_version or MAX_SUPPORTED_VERSION

    @property  # type: ignore[misc]
    @requires_version(2, 0)
    def api_version(self) -> APIVersion:
        """The API version the protocol is using.

        See :ref:`versioning` for more information
        """
        return self._api_version

    @requires_version(2, 0)
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
