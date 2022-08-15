import pytest
from decoy import Decoy

from opentrons.protocol_api import ProtocolContext
from opentrons.protocol_api._core import (
    AbstractProtocolCore as ProtocolCore,
    AbstractLabwareCore as LabwareCore,
)


@pytest.fixture
def core(decoy: Decoy) -> ProtocolCore:
    """Get a mocked out protocol implementation core."""
    return decoy.mock(cls=ProtocolCore)


@pytest.fixture
def labware_core(decoy: Decoy) -> LabwareCore:
    """Get a mocked out labware implementation core."""
    return decoy.mock(cls=LabwareCore)


@pytest.fixture
def subject(core: ProtocolCore) -> ProtocolContext:
    """Get a ProtocolContext test subject with its dependencies mocked out."""
    return ProtocolContext(core=core)


def test_load_labware(
    decoy: Decoy,
    core: ProtocolCore,
    labware_core: LabwareCore,
    subject: ProtocolContext,
) -> None:
    """It should load labware into a location."""
    decoy.when(core.load_labware("cool load name", "3")).then_return(labware_core)
    decoy.when(labware_core.load_name).then_return("cool load name")

    result = subject.load_labware(load_name="cool load name", location="3")

    assert result.load_name == "cool load name"
