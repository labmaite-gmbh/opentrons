"""Test for Calibration Set Up Position Implementation."""
from decoy import Decoy
import pytest
import mock

from opentrons.protocol_engine.commands.calibration.calibration_set_up_position import (
    CalibrationPositions,
    CalibrationSetUpPositionParams,
    CalibrationSetUpPositionImplementation,
    CalibrationSetUpPositionResult,
)
from opentrons.protocol_engine.execution import MovementHandler
from opentrons.protocol_engine.state import StateView
from opentrons.protocol_engine.types import DeckPoint
from opentrons.types import DeckSlotName, Point


start_calibration = DeckPoint(x=4, y=5, z=6)
probe_interation = DeckPoint(x=1, y=2, z=3)


def mock_deck_slot_center(slot_name: DeckSlotName) -> Point:
    """Return a point value for each deck slot input."""
    if slot_name == DeckSlotName.SLOT_2:
        return Point(1, 2, 3)
    elif slot_name == DeckSlotName.SLOT_5:
        return Point(4, 5, 6)
    else:
        return Point(7, 8, 9)


@pytest.mark.parametrize(
    argnames=["slot_name", "movement_coordinates"],
    argvalues=[
        [CalibrationPositions.start_calibration, start_calibration],
        [CalibrationPositions.probe_interaction, probe_interation],
    ],
)
async def test_calibration_set_up_position_implementation(
    decoy: Decoy,
    state_view: StateView,
    movement: MovementHandler,
    slot_name: CalibrationPositions,
    movement_coordinates: DeckPoint,
) -> None:
    """Command should get a Point value for a given deck slot center and \
        call Movement.move_to_coordinates with the correct input."""
    subject = CalibrationSetUpPositionImplementation(
        state_view=state_view, movement=movement
    )

    params = CalibrationSetUpPositionParams(
        pipetteId="pipette-id",
        slot_name=slot_name,
    )
    decoy.when(state_view.labware.get_slot_center_position()).then_return(mock_deck_slot_center) 
        state_view.labware, "get_slot_center_position", new=mock_deck_slot_center
    ):
        result = await subject.execute(params=params)

    assert result == CalibrationSetUpPositionResult()

    decoy.verify(
        await movement.move_to_coordinates(
            pipette_id="pipette-id",
            deck_coordinates=movement_coordinates,
            direct=True,
            additional_min_travel_z=0,
        )
    )
