"""OT3 Hardware Controller Backend."""

from __future__ import annotations
import asyncio
from contextlib import contextmanager
import logging
from typing import (
    Dict,
    List,
    Optional,
    Tuple,
    TYPE_CHECKING,
    Sequence,
    Generator,
    cast,
    Set,
)

from opentrons.config.types import OT3Config
from opentrons.drivers.rpi_drivers.gpio_simulator import SimulatingGPIOCharDev
from opentrons.types import Mount
from opentrons.config import pipette_config
from . import ot3utils

try:
    import aionotify  # type: ignore[import]
except (OSError, ModuleNotFoundError):
    aionotify = None

try:
    from opentrons_hardware.drivers.can_bus import CanMessenger, DriverSettings
    from opentrons_hardware.drivers.can_bus.abstract_driver import AbstractCanDriver
    from opentrons_hardware.drivers.can_bus.build import build_driver
    from opentrons_hardware.hardware_control.move_group_runner import MoveGroupRunner
    from opentrons_hardware.hardware_control.motion_planning import (
        Move,
        Coordinates,
    )

    from opentrons_hardware.hardware_control.network import probe
    from opentrons_ot3_firmware.constants import NodeId
    from opentrons_ot3_firmware.messages.message_definitions import (
        SetupRequest,
        EnableMotorRequest,
    )
    from opentrons_ot3_firmware.messages.payloads import EmptyPayload
except ModuleNotFoundError:
    pass

from opentrons.hardware_control.module_control import AttachedModulesControl
from opentrons.hardware_control.types import BoardRevision, Axis, AionotifyEvent

if TYPE_CHECKING:
    from opentrons_shared_data.pipette.dev_types import PipetteName, PipetteModel
    from ..dev_types import (
        AttachedInstruments,
        AttachedInstrument,
        InstrumentHardwareConfigs,
    )
    from opentrons.drivers.rpi_drivers.dev_types import GPIODriverLike

log = logging.getLogger(__name__)


AxisValueMap = Dict[str, float]

_FIXED_PIPETTE_ID: str = "P1KSV3120211118A01"
_FIXED_PIPETTE_NAME: PipetteName = "p1000_single_gen3"
_FIXED_PIPETTE_MODEL: PipetteModel = cast("PipetteModel", "p1000_single_v3.0")


class OT3Controller:
    """OT3 Hardware Controller Backend."""

    _messenger: CanMessenger
    _position: Dict[NodeId, float]

    @classmethod
    async def build(cls, config: OT3Config) -> OT3Controller:
        """Create the OT3Controller instance.

        Args:
            config: Robot configuration

        Returns:
            Instance.
        """
        driver = await build_driver(DriverSettings())
        return cls(config, driver=driver)

    def __init__(self, config: OT3Config, driver: AbstractCanDriver) -> None:
        """Construct.

        Args:
            config: Robot configuration
            driver: The Can Driver
        """
        self._configuration = config
        self._gpio_dev = SimulatingGPIOCharDev("simulated")
        self._module_controls: Optional[AttachedModulesControl] = None
        self._messenger = CanMessenger(driver=driver)
        self._messenger.start()
        self._position = self._get_home_position()
        try:
            self._event_watcher = self._build_event_watcher()
        except AttributeError:
            log.warning(
                "Failed to initiate aionotify, cannot watch modules "
                "or door, likely because not running on linux"
            )
        self._present_nodes: Set[NodeId] = set()

    async def setup_motors(self) -> None:
        """Set up the motors."""
        await self._messenger.send(
            node_id=NodeId.broadcast,
            message=SetupRequest(payload=EmptyPayload()),
        )
        await self._messenger.send(
            node_id=NodeId.broadcast,
            message=EnableMotorRequest(payload=EmptyPayload()),
        )

    @property
    def gpio_chardev(self) -> GPIODriverLike:
        """Get the GPIO device."""
        return self._gpio_dev

    @property
    def board_revision(self) -> BoardRevision:
        """Get the board revision"""
        return BoardRevision.UNKNOWN

    @property
    def module_controls(self) -> AttachedModulesControl:
        """Get the module controls."""
        if self._module_controls is None:
            raise AttributeError("Module controls not found.")
        return self._module_controls

    @module_controls.setter
    def module_controls(self, module_controls: AttachedModulesControl) -> None:
        """Set the module controls"""
        self._module_controls = module_controls

    def is_homed(self, axes: Sequence[str]) -> bool:
        return True

    async def update_position(self) -> AxisValueMap:
        """Get the current position."""
        return self._axis_convert(self._position)

    @staticmethod
    def _axis_convert(position: Dict[NodeId, float]) -> AxisValueMap:
        ret: AxisValueMap = {"A": 0, "B": 0, "C": 0, "X": 0, "Y": 0, "Z": 0}
        for node, pos in position.items():
            # we need to make robot config apply to z or in some other way
            # reflect the sense of the axis direction
            if ot3utils.node_is_axis(node):
                ret[ot3utils.node_to_axis(node)] = pos
        log.info(f"update_position: {ret}")
        return ret

    async def move(
        self,
        origin: "Coordinates",
        moves: List["Move"],
    ) -> None:
        """Move to a position.

        Args:
            target_position: Map of axis to position.
            home_flagged_axes: Whether to home afterwords.
            speed: Optional speed
            axis_max_speeds: Optional map of axis to speed.

        Returns:
            None
        """
        move_group, final_positions = ot3utils.create_move_group(
            origin, moves, self._present_nodes
        )
        runner = MoveGroupRunner(move_groups=[move_group])
        await runner.run(can_messenger=self._messenger)
        self._position.update(final_positions)

    async def home(self, axes: Optional[List[str]] = None) -> AxisValueMap:
        """Home axes.

        Args:
            axes: Optional list of axes.

        Returns:
            Homed position.
        """
        return self._axis_convert(self._position)

    async def fast_home(self, axes: Sequence[str], margin: float) -> AxisValueMap:
        """Fast home axes.

        Args:
            axes: List of axes to home.
            margin: Margin

        Returns:
            New position.
        """
        return self._axis_convert(self._position)

    async def get_attached_instruments(
        self, expected: Dict[Mount, PipetteName]
    ) -> AttachedInstruments:
        """Get attached instruments.

        Args:
            expected: Which mounts are expected.

        Returns:
            A map of mount to pipette name.
        """
        if expected.get(Mount.LEFT) and expected.get(Mount.LEFT) != _FIXED_PIPETTE_NAME:
            raise RuntimeError(f"only support {_FIXED_PIPETTE_NAME}  right now")

        return {
            Mount.LEFT: {
                "config": pipette_config.load(_FIXED_PIPETTE_MODEL, _FIXED_PIPETTE_ID),
                "id": _FIXED_PIPETTE_ID,
            }
        }

    def set_active_current(self, axis_currents: Dict[Axis, float]) -> None:
        """Set the active current.

        Args:
            axis_currents: Axes' currents

        Returns:
            None
        """
        return None

    @contextmanager
    def save_current(self) -> Generator[None, None, None]:
        """Save the current."""
        yield

    @staticmethod
    def _build_event_watcher():
        watcher = aionotify.Watcher()
        watcher.watch(
            alias="modules",
            path="/dev",
            flags=(aionotify.Flags.CREATE | aionotify.Flags.DELETE),
        )
        return watcher

    async def _handle_watch_event(self):
        try:
            event = await self._event_watcher.get_event()
        except asyncio.IncompleteReadError:
            log.debug("incomplete read error when quitting watcher")
            return
        if event is not None:
            if "ot_module" in event.name:
                event_name = event.name
                flags = aionotify.Flags.parse(event.flags)
                event_description = AionotifyEvent.build(event_name, flags)
                await self.module_controls.handle_module_appearance(event_description)

    async def watch(self, loop: asyncio.AbstractEventLoop):
        can_watch = aionotify is not None
        if can_watch:
            await self._event_watcher.setup(loop)

        while can_watch and (not self._event_watcher.closed):
            await self._handle_watch_event()

    @property
    def axis_bounds(self) -> Dict[Axis, Tuple[float, float]]:
        """Get the axis bounds."""
        # TODO (AL, 2021-11-18): The bounds need to be defined
        phony_bounds = (0, 10000)
        return {
            Axis.A: phony_bounds,
            Axis.B: phony_bounds,
            Axis.C: phony_bounds,
            Axis.X: phony_bounds,
            Axis.Y: phony_bounds,
            Axis.Z: phony_bounds,
        }

    @property
    def fw_version(self) -> Optional[str]:
        """Get the firmware version."""
        return None

    async def update_firmware(
        self, filename: str, loop: asyncio.AbstractEventLoop, modeset: bool
    ) -> str:
        """Update the firmware."""
        return "Done"

    def engaged_axes(self) -> Dict[str, bool]:
        """Get engaged axes."""
        return {}

    async def disengage_axes(self, axes: List[str]) -> None:
        """Disengage axes."""
        return None

    def set_lights(self, button: Optional[bool], rails: Optional[bool]) -> None:
        """Set the light states."""
        return None

    def get_lights(self) -> Dict[str, bool]:
        """Get the light state."""
        return {}

    def pause(self) -> None:
        """Pause the controller activity."""
        return None

    def resume(self) -> None:
        """Resume the controller activity."""
        return None

    async def halt(self) -> None:
        """Halt the motors."""
        return None

    async def hard_halt(self) -> None:
        """Halt the motors."""
        return None

    async def probe(self, axis: str, distance: float) -> AxisValueMap:
        """Probe."""
        return {}

    def clean_up(self) -> None:
        """Clean up."""

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            return

        if hasattr(self, "_event_watcher"):
            if loop.is_running() and self._event_watcher:
                self._event_watcher.close()
        return None

    async def configure_mount(
        self, mount: Mount, config: InstrumentHardwareConfigs
    ) -> None:
        """Configure a mount."""
        return None

    @staticmethod
    def _get_home_position() -> Dict[NodeId, float]:
        return {
            NodeId.head_l: 0,
            NodeId.head_r: 0,
            NodeId.gantry_x: 0,
            NodeId.gantry_y: 0,
            NodeId.pipette_left: 0,
            NodeId.pipette_right: 0,
        }

    async def probe_network(self, timeout: float = 5.0) -> None:
        """Update the list of nodes present on the network.

        The stored result is used to make sure that move commands include entries
        for all present axes, so none incorrectly move before the others are ready.
        """
        # TODO: Only add pipette ids to expected if the head indicates
        # they're present. In the meantime, we'll use get_attached_instruments to
        # see if we should expect instruments to be present, which should be removed
        # when that method actually does canbus stuff
        instrs = await self.get_attached_instruments({})
        expected = set((NodeId.gantry_x, NodeId.gantry_y, NodeId.head))
        if instrs.get(Mount.LEFT, cast("AttachedInstrument", {})).get("config", None):
            expected.add(NodeId.pipette_left)
        if instrs.get(Mount.RIGHT, cast("AttachedInstrument", {})).get("config", None):
            expected.add(NodeId.pipette_right)
        present = await probe(self._messenger, expected, timeout)
        if NodeId.head in present:
            present.remove(NodeId.head)
            present.add(NodeId.head_r)
            present.add(NodeId.head_l)
        self._present_nodes = present