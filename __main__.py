#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Joao Carlos Bastos Portela"
__license__ = "GPLv3"
__version__ = "0.0.2"
__maintainer__ = "Joao Carlos Bastos Portela"
__email__ = "jcbastosportela@gmail.com"
__status__ = "Production"

from pystray import MenuItem, Menu, Icon
from typing import List, Tuple, Callable
from types import MethodType
from PIL import Image
import os
import argparse

import displays
import inputs

import logging

# General logging settings
FORMAT = '%(asctime)s - %(levelname)s - %(filename)s:%(funcName)s - %(message)s'
logging.basicConfig(level=logging.ERROR, format=FORMAT)

# logging for this file
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

_ROOT_PATH = os.path.normpath(os.path.dirname(__file__))
_RES_DIR = os.path.join(_ROOT_PATH, 'res')
_ICON_PATH = os.path.join(_RES_DIR, 'huion_icon.png')

class HuionDisplaySelector(object):
    """Handles the display selection for Huion devices
    """
    def __init__(self, device_name_match:str)->None:
        self.__available_displays = displays.get_available_output_displays()
        self.__huion_devices = inputs.get_huion_pointer_devices(device_name_match)

        self.__output_display_options: List[Tuple[str,Callable]]  = []
        self.__huion_devices_options: List[Tuple[str,Callable]] = []

        self._selected_huion_device_id: int = None
        if len(self.__huion_devices) > 0:
            self._selected_huion_device_id = self.__huion_devices[0].xinput_id  # use the first Huion by default
        
        for available_display in self.__available_displays:
            #start on the main display by default
            if not self._selected_huion_device_id is None and available_display.is_main:
                inputs.map_input_device_to_output(self._selected_huion_device_id, available_display.name)

            clean_name = ''.join(filter(str.isalnum, available_display.name)) 
            exec(
        f"""
def map_input_device_to_{clean_name}(self)->None:
    inputs.map_input_device_to_output(self._selected_huion_device_id, '{available_display.name}')
            """
            )
            action_cb_name = f'map_input_device_to_{clean_name}'
            setattr(
                HuionDisplaySelector,
                action_cb_name,
                MethodType(
                    locals()[action_cb_name],
                    self
                    )
            )
            self.__output_display_options.append((available_display.name, getattr(self, action_cb_name)))

        for huion_device in self.__huion_devices:
            clean_name = ''.join(filter(str.isalnum, huion_device.name)) 
            exec(
        f"""
def select_huion_{clean_name}(self)->None:
    self._selected_huion_device_id = {huion_device.xinput_id}
            """
            )
            action_cb_name = f'select_huion_{clean_name}'
            setattr(
                HuionDisplaySelector,
                f'select_huion_{clean_name}',
                MethodType(
                    locals()[action_cb_name],
                    self
                    )
            )
            self.__huion_devices_options.append((huion_device.name, getattr(self, action_cb_name)))

    @property
    def output_display_options(self)->List[Tuple[str,Callable]]:
        return self.__output_display_options
    
    @property
    def huion_devices_options(self)->List[Tuple[str,Callable]]:
        return self.__huion_devices_options


def run_huion_screen_selector(device_name_match:str)->None:
    """Runs the Huion Screen Selector system tray app

    Args:
        device_name_match (str): String for matching with the devices names returned by xinput
    """
    huion_disp_sel = HuionDisplaySelector(device_name_match)

    # get menu entries for the available displays
    menu_displays =[]
    for display in huion_disp_sel.output_display_options:
        menu_displays.append(
            MenuItem(display[0], display[1])
        )

    # get menu entries for available huion tablets
    menu_select_huion = []
    for device in huion_disp_sel.huion_devices_options:
        print(device)
        menu_select_huion.append(
            MenuItem(device[0], device[1])
        )
    if len(menu_select_huion) == 0:
        menu_select_huion.append('Enter device name match', )

    def exit_prg()->None:
        """exits the system tray application
        """
        icon.stop()

    # create full menu
    menu = [
            MenuItem('Huion Device', Menu(*menu_select_huion)),
            MenuItem('Select Monitor', Menu(*menu_displays)),
            MenuItem('_______', None),
            MenuItem('Quit', exit_prg)
            ]

    image = Image.open(_ICON_PATH)
    icon = Icon("HuionScreenSelector", image, "", menu)
    icon.run()


if __name__ == '__main__':
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument('-d', '--device', default='', help='String for matching with the devices names returned by xinput. If nothing passed all the available input devices will be listed as Huion devices.')
    args = args_parser.parse_args()

    print(args.device)
    run_huion_screen_selector(args.device)


