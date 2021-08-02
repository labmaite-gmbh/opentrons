"""Tests for a JsonFileRunner interface."""
import pytest
from decoy import Decoy
from pathlib import Path

from opentrons.file_runner import JsonFileRunner, ProtocolFile, ProtocolFileType
from opentrons.file_runner.json_file_reader import JsonFileReader
from opentrons.file_runner.json_command_translator import CommandTranslator

from opentrons.protocol_engine import ProtocolEngine, WellLocation
from opentrons.protocol_engine import commands as pe_commands
from opentrons.protocols.models import JsonProtocol


@pytest.fixture
def protocol_engine(decoy: Decoy) -> ProtocolEngine:
    """Create a protocol engine fixture."""
    return decoy.mock(cls=ProtocolEngine)


@pytest.fixture
def command_translator(decoy: Decoy) -> CommandTranslator:
    """Create a stubbed command translator fixture."""
    return decoy.mock(cls=CommandTranslator)


@pytest.fixture
def file_reader(
    decoy: Decoy,
    protocol_file: ProtocolFile,
    json_protocol: JsonProtocol,
) -> JsonFileReader:
    """Create a stubbed JsonFileReader interface."""
    reader = decoy.mock(cls=JsonFileReader)

    decoy.when(reader.read(protocol_file)).then_return(json_protocol)

    return reader


@pytest.fixture
def protocol_file(decoy: Decoy) -> ProtocolFile:
    """Get a JsonProtocolFile value fixture."""
    return ProtocolFile(file_type=ProtocolFileType.JSON, file_path=Path("/dev/null"))


@pytest.fixture
def subject(
    protocol_file: ProtocolFile,
    protocol_engine: ProtocolEngine,
    file_reader: JsonFileReader,
    command_translator: CommandTranslator,
) -> JsonFileRunner:
    """Get a JsonFileRunner test subject."""
    return JsonFileRunner(
        file=protocol_file,
        file_reader=file_reader,
        protocol_engine=protocol_engine,
        command_translator=command_translator,
    )


async def test_json_runner_run(
    decoy: Decoy,
    subject: JsonFileRunner,
    protocol_engine: ProtocolEngine,
) -> None:
    """It should be able to run the protocol until done."""
    await subject.run()

    decoy.verify(
        protocol_engine.play(),
        await protocol_engine.stop(wait_until_complete=True),
    )


def test_json_runner_load_commands_to_engine(
    decoy: Decoy,
    json_protocol: JsonProtocol,
    subject: JsonFileRunner,
    command_translator: CommandTranslator,
    protocol_engine: ProtocolEngine,
) -> None:
    """It should send translated commands to protocol engine."""
    mock_cmd1 = pe_commands.PickUpTipRequest(
        data=pe_commands.PickUpTipData(
            pipetteId="123",
            labwareId="abc",
            wellName="def",
        )
    )
    mock_cmd2 = pe_commands.AspirateRequest(
        data=pe_commands.AspirateData(
            volume=321,
            wellLocation=WellLocation(),
            pipetteId="123",
            labwareId="xyz",
            wellName="def",
        )
    )
    mock_cmd3 = pe_commands.DispenseRequest(
        data=pe_commands.DispenseData(
            volume=321,
            wellLocation=WellLocation(),
            pipetteId="123",
            labwareId="xyz",
            wellName="def",
        )
    )

    decoy.when(command_translator.translate(json_protocol)).then_return(
        [mock_cmd1, mock_cmd2, mock_cmd3]
    )

    subject.load()

    decoy.verify(
        protocol_engine.add_command(mock_cmd1),
        protocol_engine.add_command(mock_cmd2),
        protocol_engine.add_command(mock_cmd3),
    )
