from __future__ import annotations

from .abstract_cores import AbstractProtocolCore, AbstractLabwareCore


class LegacyProtocolCore(AbstractProtocolCore):
    def load_labware(self, load_name: str, location: str) -> AbstractLabwareCore:
        raise NotImplementedError("LegacyProtocolCore not implemented")


class LegacyLabwareCore(AbstractLabwareCore):
    @property
    def load_name(self) -> str:
        raise NotImplementedError("LegacyLabwareCore not implemented")
