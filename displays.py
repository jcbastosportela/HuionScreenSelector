from dataclasses import dataclass
from typing import List
import subprocess
import re
import logging

# General logging settings
FORMAT = '%(asctime)s - %(levelname)s - %(filename)s:%(funcName)s - %(message)s'
logging.basicConfig(level=logging.ERROR, format=FORMAT)

# logging for this file
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class ExecError(Exception):
    """Error when execution on a command fails
    """
    pass

class BadResult(Exception):
    """Error when the output of the execution of a command is bad
    """
    pass


@dataclass
class Display:
    """Represents the entry of one display
    """
    name: str
    code_name: str
    xrandr_index: int
    is_main: bool
    resolution: str


def get_available_output_displays() -> List[Display]:
    """Gets the list of active displays
    Raises:
        ExecError: if getting active displays fails
        BadResult: if the result is bad

    Returns:
        List[Display]: List of currently active monitors
    """
    xrandr_cmd = ['xrandr', '--listactivemonitors']
    try:
        active_displays = subprocess.check_output(xrandr_cmd)
    except Exception as e:
        raise ExecError(e)
    try:
        active_displays = active_displays.decode().splitlines()
        active_displays = active_displays[1:]   # the first line is the count of active displays
        active_displays = [active_display.strip() for active_display in active_displays]

        ret = []
        pattern = re.compile('(\d):\s+(\S+)\s+(\S+)\s+(\S+)')
        for active_display in active_displays:
            data = pattern.search(active_display)
            if len(data.groups()) != 4:
                raise BadResult(f'Xrandr returned wrong formated output. {active_display}')
            is_main = "*" in data.group(2)
            disp = Display(data.group(4), data.group(2),int(data.group(1)), is_main, data.group(3))
            ret.append(disp)

    except Exception as e:
        raise BadResult(e)
    return ret