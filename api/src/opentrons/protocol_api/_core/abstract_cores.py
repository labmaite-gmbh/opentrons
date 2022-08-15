from __future__ import annotations

from abc import ABC, abstractmethod


class AbstractProtocolCore(ABC):
    @abstractmethod
    def load_labware(self, load_name: str, location: str) -> AbstractLabwareCore:
        ...


class AbstractLabwareCore(ABC):
    @property
    @abstractmethod
    def load_name(self) -> str:
        ...
