import pytest
from decoy import Decoy

from opentrons.protocol_api import MAX_SUPPORTED_VERSION, APIVersion, ProtocolContext
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


def test_api_version(core: ProtocolCore) -> None:
    """It should have an API version."""
    subject = ProtocolContext(core=core, api_version=None)
    assert subject.api_version == MAX_SUPPORTED_VERSION

    subject = ProtocolContext(core=core, api_version=APIVersion(2, 0))
    assert subject.api_version == APIVersion(2, 0)


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
