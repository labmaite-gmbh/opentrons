"""Run control side-effect handler."""
from datetime import datetime

import pytest
from decoy import Decoy, matchers

from opentrons.protocol_engine.state import StateStore
from opentrons.protocol_engine.actions import ActionDispatcher, PauseAction, PauseSource
from opentrons.protocol_engine.execution.run_control import RunControlHandler
from opentrons.protocol_engine.state import EngineConfigs


@pytest.fixture
def mock_state_store(decoy: Decoy) -> StateStore:
    """Get a mocked out StateStore."""
    return decoy.mock(cls=StateStore)


@pytest.fixture
def mock_action_dispatcher(decoy: Decoy) -> ActionDispatcher:
    """Get a mocked out ActionDispatcher."""
    return decoy.mock(cls=ActionDispatcher)


@pytest.fixture
def subject(
    mock_state_store: StateStore,
    mock_action_dispatcher: ActionDispatcher,
) -> RunControlHandler:
    """Create a RunControlHandler with its dependencies mocked out."""
    return RunControlHandler(
        state_store=mock_state_store,
        action_dispatcher=mock_action_dispatcher,
    )


async def test_pause(
    decoy: Decoy,
    mock_state_store: StateStore,
    mock_action_dispatcher: ActionDispatcher,
    subject: RunControlHandler,
) -> None:
    """It should be able to execute a pause."""
    decoy.when(mock_state_store.get_configs()).then_return(
        EngineConfigs(ignore_pause=False)
    )
    await subject.wait_for_resume()
    decoy.verify(
        mock_action_dispatcher.dispatch(PauseAction(source=PauseSource.PROTOCOL)),
        await mock_state_store.wait_for(
            condition=mock_state_store.commands.get_is_running
        ),
    )


async def test_pause_analysis(
    decoy: Decoy,
    mock_state_store: StateStore,
    mock_action_dispatcher: ActionDispatcher,
    subject: RunControlHandler,
) -> None:
    """It should no op during a protocol analysis."""
    decoy.when(mock_state_store.get_configs()).then_return(
        EngineConfigs(ignore_pause=True)
    )
    await subject.wait_for_resume()
    decoy.verify(
        mock_action_dispatcher.dispatch(PauseAction(source=matchers.Anything())),
        times=0,
    )


async def test_wait_for_duration(
    decoy: Decoy,
    mock_state_store: StateStore,
    subject: RunControlHandler,
) -> None:
    """It should wait for a specified duration.

    This test mixes mocks and actual functionality.
    An implementation that is "more testabe" probably involves
    re-implementing `asyncio.sleep`, which just isn't worth it.
    """
    decoy.when(mock_state_store.get_configs()).then_return(
        EngineConfigs(ignore_pause=False)
    )
    start = datetime.now()
    await subject.wait_for_duration(seconds=0.1)
    end = datetime.now()

    # NOTE: margin of error selected empirically
    # this is flakey test risk in CI
    assert (end - start).total_seconds() == pytest.approx(0.1, abs=0.05)


async def test_wait_for_duration_ignore_pause(
    decoy: Decoy,
    mock_state_store: StateStore,
    subject: RunControlHandler,
) -> None:
    """It should wait for a specified duration.

    This test mixes mocks and actual functionality.
    An implementation that is "more testabe" probably involves
    re-implementing `asyncio.sleep`, which just isn't worth it.
    """
    decoy.when(mock_state_store.get_configs()).then_return(
        EngineConfigs(ignore_pause=True)
    )
    start = datetime.now()
    await subject.wait_for_duration(seconds=0.1)
    end = datetime.now()

    # NOTE: margin of error selected empirically
    # this is flakey test risk in CI
    assert (end - start).total_seconds() == pytest.approx(0, abs=0.05)
