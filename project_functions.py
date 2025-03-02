import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from aes_key_and_iv_creation import key_creation_for_aes, iv_creation_for_aes
from Crypto.Random import get_random_bytes
import win32con
import win32api

secure_directory = os.path.join(os.path.dirname(__file__), 'Secure Data')


def decrypt_directory():
    data_file = os.path.join(secure_directory, 'key_and_iv.txt')
    key_salt_file = os.path.join(secure_directory, 'key_salt.txt')
    iv_salt_file = os.path.join(secure_directory, 'iv_salt.txt')

    if not os.path.exists(secure_directory):
        os.makedirs(secure_directory)

    if not os.path.exists(key_salt_file):
        key_salt = get_random_bytes(32)
        key = key_creation_for_aes(key_salt)
        with open(key_salt_file, 'w') as file:
            file.write(f"Key salt: {key_salt.hex()}\n")
    else:
        with open(key_salt_file, 'r') as file:
            key_salt_line = file.readline().strip()
            key_salt = bytes.fromhex(key_salt_line.split(':')[1].strip())
            key = key_creation_for_aes(key_salt)
        open(key_salt_file, 'w').close()

        with open(key_salt_file, 'w') as file:
            file.write(f'Key salt: {get_random_bytes(32).hex()}')

    if not os.path.exists(iv_salt_file):
        iv_salt = get_random_bytes(16)
        iv = iv_creation_for_aes(iv_salt)
        with open(iv_salt_file, 'w') as file:
            file.write(f"IV salt: {iv_salt.hex()}\n")
    else:
        with open(iv_salt_file, 'r') as file:
            iv_salt_line = file.readline().strip()
            iv_salt = bytes.fromhex(iv_salt_line.split(':')[1].strip())
            iv = iv_creation_for_aes(iv_salt)
        open(iv_salt_file, 'w').close()

        with open(iv_salt_file, 'w') as file:
            file.write(f'IV salt: {get_random_bytes(16).hex()}')

    if not os.path.exists(data_file):
        with open(data_file, 'w') as key_and_iv:
            with open(key_salt_file, 'r') as keysalt:
                key_salt_line = keysalt.readline().strip()
                key_salt = bytes.fromhex(key_salt_line.split(':')[1].strip())
                key_and_iv.write(f"Key: {key_creation_for_aes(key_salt).hex()}\n")
            with open(iv_salt_file, 'r') as ivsalt:
                iv_salt_line = ivsalt.readline().strip()
                iv_salt = bytes.fromhex(iv_salt_line.split(':')[1].strip())
                key_and_iv.write(f"IV: {iv_creation_for_aes(iv_salt).hex()}\n")

    win32api.SetFileAttributes(data_file, win32con.FILE_ATTRIBUTE_HIDDEN)
    win32api.SetFileAttributes(key_salt_file, win32con.FILE_ATTRIBUTE_HIDDEN)
    win32api.SetFileAttributes(iv_salt_file, win32con.FILE_ATTRIBUTE_HIDDEN)

    for filename in os.listdir(secure_directory):
        if filename == 'key_and_iv.txt' or filename == 'iv_salt.txt' or filename == 'key_salt.txt':
            continue

        input_path = os.path.join(secure_directory, filename)
        output_path = os.path.join(secure_directory, filename[:-4])

        with open(input_path, 'rb') as file:
            ciphertext = file.read()

            cipher = AES.new(key, AES.MODE_CBC, iv)

        decrypted_data = cipher.decrypt(ciphertext)

        if len(decrypted_data) > 0:
            unpadded_data = unpad(decrypted_data, AES.block_size)

            with open(output_path, 'wb') as file:
                file.write(unpadded_data)
                os.remove(input_path)


def encrypt_directory():
    key = b''
    iv = b''
    if not os.path.exists(secure_directory):
        os.makedirs(secure_directory)

    key_and_iv_file = os.path.join(secure_directory, 'key_and_iv.txt')
    if os.path.exists(key_and_iv_file):
        with open(key_and_iv_file, 'r') as key_iv:
            key_line = key_iv.readline().strip()
            iv_line = key_iv.readline().strip()

            key = bytes.fromhex(key_line.split(':')[1].strip())
            iv = bytes.fromhex(iv_line.split(':')[1].strip())

        os.remove(key_and_iv_file)

    for filename in os.listdir(secure_directory):
        if filename == 'iv_salt.txt' or filename == 'key_salt.txt':
            continue
        input_path = os.path.join(secure_directory, filename)
        output_path = os.path.join(secure_directory, filename + '.enc')

        with open(input_path, 'rb') as file:
            plaintext = file.read()

        cipher = AES.new(key, AES.MODE_CBC, iv)

        padded_plaintext = pad(plaintext, AES.block_size)

        ciphertext = cipher.encrypt(padded_plaintext)

        with open(output_path, 'wb') as file:
            file.write(ciphertext)
            os.remove(input_path)
        key = b''
        iv = b''
