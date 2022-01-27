import logging
from typing import List
from opentrons.util.helpers import utc_now

log = logging.getLogger(__name__)

timing_results: List[str] = []


def start_perf_recording() -> None:
    global timing_results
    timing_results = []


def stop_perf_recording() -> None:
    global timing_results

    msg = "\n".join(
        [
            "================",
            "label, phase, timestamp",
            "\n".join(timing_results),
            "================",
        ]
    )

    log.error(msg)


def timestamp(label: str, phase: str) -> None:
    stamp = f"{label}, {phase}, {utc_now().isoformat()}"
    timing_results.append(stamp)
