import logging
from typing import Optional

from opentrons.drivers.smoothie_drivers.driver_3_0 import GCODE

from .command_processor import CommandProcessor

logger = logging.getLogger(__name__)

v = """Build version: EMULATOR, Build date: CURRENT, MCU: NONE, System Clock: NONE"""


class SmoothieEmulator(CommandProcessor):
    """Smoothie emulator"""

    def __init__(self) -> None:
        self.x = self.y = self.z = self.a = self.b = self.c = 0.00

    def handle(self, cmd: str, payload: str) -> Optional[str]:
        """Handle a command."""
        logger.info(f"Got command {cmd}")
        if GCODE.HOMING_STATUS == cmd:
            return "X:0 Y:0 Z:0 A:0 B:0 C:0"
        elif GCODE.CURRENT_POSITION == cmd:
            return f"{cmd}\r\n\r\nok MCS: X:{self.x} Y:{self.y} " \
                   f"Z:{self.z} A:{self.a} B:{self.b} C:{self.c}"
        elif GCODE.VERSION == cmd:
            return v
        return None