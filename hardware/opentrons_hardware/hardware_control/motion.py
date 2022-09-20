"""A collection of motions that define a single move."""
from typing import List, Dict, Iterable, Union
from dataclasses import dataclass
import numpy as np
from logging import getLogger
from enum import Enum, unique
from opentrons_hardware.firmware_bindings.constants import NodeId, PipetteTipActionType

LOG = getLogger(__name__)


NodeIdMotionValues = Dict[NodeId, np.float64]


@unique
class MoveStopCondition(int, Enum):
    """Move Stop Condition."""

    none = 0x0
    limit_switch = 0x1
    cap_sensor = 0x2
    encoder_position = 0x4
    gripper_force = 0x5


@unique
class MoveType(int, Enum):
    """Move Type."""

    linear = 0x0
    home = 0x1
    calibration = 0x2
    grip = 0x3

    @classmethod
    def get_move_type(cls, condition: MoveStopCondition) -> "MoveType":
        """Return the Move Type for the given Stop Condition."""
        mapping = {
            MoveStopCondition.none: cls.linear,
            MoveStopCondition.limit_switch: cls.home,
            MoveStopCondition.cap_sensor: cls.calibration,
            MoveStopCondition.encoder_position: cls.linear,
            MoveStopCondition.gripper_force: cls.grip,
        }
        return mapping[condition]


@dataclass(frozen=True)
class MoveGroupSingleAxisStep:
    """A single move in a move group."""

    distance_mm: np.float64
    velocity_mm_sec: np.float64
    duration_sec: np.float64
    acceleration_mm_sec_sq: np.float64 = np.float64(0)
    stop_condition: MoveStopCondition = MoveStopCondition.none
    move_type: MoveType = MoveType.linear


@dataclass(frozen=True)
class MoveGroupTipActionStep:
    """A single tip handling action that requires movement in a move group."""

    velocity_mm_sec: np.float64
    duration_sec: np.float64
    action: PipetteTipActionType
    stop_condition: MoveStopCondition


@dataclass(frozen=True)
class MoveGroupSingleGripperStep:
    """A single gripper move in a move group."""

    duration_sec: np.float64
    pwm_duty_cycle: np.float32
    encoder_position_um: np.int32
    pwm_frequency: np.float32 = np.float32(320000)
    stop_condition: MoveStopCondition = MoveStopCondition.gripper_force
    move_type: MoveType = MoveType.grip


SingleMoveStep = Union[
    MoveGroupSingleAxisStep, MoveGroupSingleGripperStep, MoveGroupTipActionStep
]

MoveGroupStep = Dict[
    NodeId,
    SingleMoveStep,
]

MoveGroup = List[MoveGroupStep]

MoveGroups = List[MoveGroup]

MAX_SPEEDS = {
    NodeId.gantry_x: 50,
    NodeId.gantry_y: 50,
    NodeId.head_l: 50,
    NodeId.head_r: 50,
    NodeId.pipette_left: 2,
    NodeId.pipette_right: 2,
}


def create_step(
    distance: Dict[NodeId, np.float64],
    velocity: Dict[NodeId, np.float64],
    acceleration: Dict[NodeId, np.float64],
    duration: np.float64,
    present_nodes: Iterable[NodeId],
    stop_condition: MoveStopCondition = MoveStopCondition.none,
) -> MoveGroupStep:
    """Create a move from a block.

    Args:
        origin: Start position.
        target: Target position.
        speed: the speed

    Returns:
        A Move
    """
    ordered_nodes = sorted(present_nodes, key=lambda node: node.value)
    step: MoveGroupStep = {}
    for axis_node in ordered_nodes:
        step[axis_node] = MoveGroupSingleAxisStep(
            distance_mm=distance.get(axis_node, np.float64(0)),
            acceleration_mm_sec_sq=acceleration.get(axis_node, np.float64(0)),
            velocity_mm_sec=velocity.get(axis_node, np.float64(0)),
            duration_sec=duration,
            stop_condition=stop_condition,
            move_type=MoveType.get_move_type(stop_condition),
        )
    return step


def create_home_step(
    distance: Dict[NodeId, np.float64], velocity: Dict[NodeId, np.float64]
) -> MoveGroupStep:
    """Creates a step for each axis to be homed."""
    step: MoveGroupStep = {}
    for axis in distance.keys():
        step[axis] = MoveGroupSingleAxisStep(
            distance_mm=distance[axis],
            acceleration_mm_sec_sq=np.float64(0),
            velocity_mm_sec=velocity[axis],
            duration_sec=abs(distance[axis] / velocity[axis]),
            stop_condition=MoveStopCondition.limit_switch,
            move_type=MoveType.home,
        )
    return step


def create_tip_action_step(
    velocity: Dict[NodeId, np.float64],
    duration: np.float64,
    present_nodes: Iterable[NodeId],
    action: PipetteTipActionType,
) -> MoveGroupStep:
    """Creates a step for tip handling actions that require motor movement."""
    ordered_nodes = sorted(present_nodes, key=lambda node: node.value)
    step: MoveGroupStep = {}
    stop_condition = (
        MoveStopCondition.limit_switch
        if action == PipetteTipActionType.drop
        else MoveStopCondition.none
    )
    for axis_node in ordered_nodes:
        step[axis_node] = MoveGroupTipActionStep(
            velocity_mm_sec=velocity.get(axis_node, np.float64(0)),
            duration_sec=duration,
            stop_condition=stop_condition,
            action=action,
        )
    return step


def create_gripper_jaw_step(
    duration: np.float64,
    duty_cycle: np.float32,
    encoder_position_um: np.int32 = np.int32(0),
    frequency: np.float32 = np.float32(320000),
    stop_condition: MoveStopCondition = MoveStopCondition.gripper_force,
    move_type: MoveType = MoveType.grip,
) -> MoveGroupStep:
    """Creates a step for gripper jaw action."""
    step: MoveGroupStep = {}
    step[NodeId.gripper_g] = MoveGroupSingleGripperStep(
        duration_sec=duration,
        pwm_frequency=frequency,
        pwm_duty_cycle=duty_cycle,
        stop_condition=stop_condition,
        move_type=move_type,
        encoder_position_um=encoder_position_um,
    )
    return step
