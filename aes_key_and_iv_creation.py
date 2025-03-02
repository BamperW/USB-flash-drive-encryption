import subprocess
import re
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def usb_flash_drive_letters_list():
    drive_letters = []
    drive_type_check = subprocess.check_output('wmic logicaldisk where drivetype=2 get deviceid', shell=True)

    for drive in str(drive_type_check).strip().split('\\r\\r\\n'):
        drive_letters_filtered = re.findall(r'\w:', drive)

        for usb_flash_drive in drive_letters_filtered:
            drive_letters.append(usb_flash_drive)
    return drive_letters


def drive_volume_serial_number():
    serial_numbers = []

    for usb_flash_drive in usb_flash_drive_letters_list():
        volume_serial_number_check = subprocess.check_output(f'vol {usb_flash_drive}', shell=True).decode()
        volume_serial_number_filter = re.findall(r'(Volume Serial Number is) (\w\w\w\w-\w\w\w\w)',
                                                 volume_serial_number_check)

        for volume_serial_number in volume_serial_number_filter:
            volume_serial_number_without_dash = volume_serial_number[1][:4] + volume_serial_number[1][5:]
            serial_numbers.append(volume_serial_number_without_dash)

    key = ''.join(serial_numbers)

    return key


def key_creation_for_aes(salt):
    incompatible_key = drive_volume_serial_number()

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000
    )

    aes_compatible_key = kdf.derive(incompatible_key.encode())
    return aes_compatible_key


def usb_flash_drive_total_size():
    drive_size_list = []
    total_drives_size = 0

    for usb_flash_drive in usb_flash_drive_letters_list():
        drive_size_check = subprocess.check_output(f'wmic logicaldisk where deviceid="{usb_flash_drive}" get size',
                                                   shell=True)

        for drive in str(drive_size_check).strip().split('\\r\\r\\n'):
            drive_size_filtered = re.findall(r'\d+', drive)
            for drive_size_string in drive_size_filtered:
                drive_size_list.append(int(drive_size_string))
                for int_drive_size in drive_size_list:
                    total_drives_size += int_drive_size

    return total_drives_size


def iv_creation_for_aes(salt):
    incompatible_iv = usb_flash_drive_total_size()

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=16,
        salt=salt,
        iterations=480000
    )

    aes_compatible_iv = kdf.derive(str(incompatible_iv).encode())
    return aes_compatible_iv
