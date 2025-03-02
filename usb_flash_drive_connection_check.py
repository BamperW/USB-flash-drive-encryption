import subprocess
from project_functions import decrypt_directory, encrypt_directory
import win32api
import win32con
import win32gui
from typing import Callable

command = 'wmic logicaldisk where drivetype=2 get  deviceid'
connection_check_output = ""


def on_usb_flash_drive_connection(none):
    global connection_check_output
    usb_flash_drive_connection_check = subprocess.check_output(command, shell=True)
    if usb_flash_drive_connection_check.strip():
        decrypt_directory()
    connection_check_output = usb_flash_drive_connection_check


def on_usb_flash_drive_disconnection(none):
    global connection_check_output
    usb_flash_drive_connection_check_on_disconnection = subprocess.check_output(command, shell=True)
    if usb_flash_drive_connection_check_on_disconnection != connection_check_output:
        encrypt_directory()


class DeviceListener:
    WM_DEVICECHANGE_EVENTS = {
        0x0019: ('DBT_CONFIGCHANGECANCELED',
                 'A request to change the current configuration (dock or undock) has been canceled.'),
        0x0018: ('DBT_CONFIGCHANGED', 'The current configuration has changed, due to a dock or undock.'),
        0x8006: ('DBT_CUSTOMEVENT', 'A custom event has occurred.'),
        0x8000: ('DBT_DEVICEARRIVAL', 'A device or piece of media has been inserted and is now available.'),
        0x8001: ('DBT_DEVICEQUERYREMOVE',
                 'Permission is requested to remove a device or piece of media. Any application can deny this request and cancel the removal.'),
        0x8002: (
            'DBT_DEVICEQUERYREMOVEFAILED', 'A request to remove a device or piece of media has been canceled.'),
        0x8004: ('DBT_DEVICEREMOVECOMPLETE', 'A device or piece of media has been removed.'),
        0x8003: ('DBT_DEVICEREMOVEPENDING', 'A device or piece of media is about to be removed. Cannot be denied.'),
        0x8005: ('DBT_DEVICETYPESPECIFIC', 'A device-specific event has occurred.'),
        0x0007: ('DBT_DEVNODES_CHANGED', 'A device has been added to or removed from the system.'),
        0x0017: (
            'DBT_QUERYCHANGECONFIG',
            'Permission is requested to change the current configuration (dock or undock).'),
        0xFFFF: ('DBT_USERDEFINED', 'The meaning of this message is user-defined.'),
    }

    def __init__(self, on_connect: Callable[[None], None], on_disconnect: Callable[[None], None]):
        self.on_connect = on_connect
        self.on_disconnect = on_disconnect

    def _create_window(self):

        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = self._on_message
        wc.lpszClassName = self.__class__.__name__
        wc.hInstance = win32api.GetModuleHandle(None)
        class_atom = win32gui.RegisterClass(wc)
        return win32gui.CreateWindow(class_atom, self.__class__.__name__, 0, 0, 0, 0, 0, 0, 0, wc.hInstance, None)

    def start(self):
        self._create_window()
        win32gui.PumpMessages()

    def _on_message(self, hwnd: int, msg: int, wparam: int, lparam: int):
        if msg != win32con.WM_DEVICECHANGE:
            return 0
        event, description = self.WM_DEVICECHANGE_EVENTS[wparam]
        if event == 'DBT_DEVICEARRIVAL':
            print("Connected!")
            self.on_connect(None)

        elif event == 'DBT_DEVICEREMOVECOMPLETE':
            print("Disconnected!")
            self.on_disconnect(None)

        return 0


if "__main__" == __name__:
    listener = DeviceListener(on_connect=on_usb_flash_drive_connection,
                              on_disconnect=on_usb_flash_drive_disconnection)
    listener.start()
