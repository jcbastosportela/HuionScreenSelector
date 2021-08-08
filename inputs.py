from os import device_encoding
import subprocess
from dataclasses import dataclass
from typing import List
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
class HuionDevice:
    """Represents on Input HUION device
    """
    name: str
    xinput_id: int
    input_type: str


def get_huion_pointer_devices() -> List[HuionDevice]:
    """Gets the list of huion devices that are pointers connected to the system

    Raises:
        ExecError: if getting devices fails
        BadResult: if the result is bad

    Returns:
        List[HuionDevice]: List of Huion pointer devices
    """
    xinput_cmd = ['xinput', 'list']
    try:
        input_devices = subprocess.check_output(xinput_cmd)
    except Exception as e:
        raise ExecError(e)
    try:
        input_devices = input_devices.decode().splitlines()
        input_devices = [input_device.strip() for input_device in input_devices]

        ret = []
        pattern = re.compile('(?:.*)↳\s+(.+)id=(\d+)\s+\[(.+)\]')
        for input_device in input_devices:
            data = pattern.search(input_device)
            if data is None:
                continue
            if len(data.groups()) != 3:
                raise BadResult(f'xinput returned wrong formated output. {input_device}')
            device_name = data.group(1).strip()
            device_id = int(data.group(2))
            input_type = data.group(3)
            if "huion" in device_name.lower() and "pointer" in input_type.lower():
                disp = HuionDevice(device_name, device_id, input_type)
                ret.append(disp)

    except Exception as e:
        raise BadResult(e)
    return ret

def map_input_device_to_output(device_id: int, output_display: str) -> None:
    xinput_map_cmd = ['xinput', 'map-to-output', f'{device_id}', output_display]
    _logger.debug(xinput_map_cmd)
    try:
        subprocess.check_output(xinput_map_cmd)
    except Exception as e:
        raise ExecError(e)
