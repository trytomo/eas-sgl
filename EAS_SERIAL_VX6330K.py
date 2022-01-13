from serial import *

PRESET_Value = 0xFFFF
POLYNOMIAL = 0x8408

test_serial = Serial('COM3', 57600, timeout=0.1)

# scan
INVENTORY1 = '06 FF 01 00 06'  # membaca TID
INVENTORY2 = '04 FF 0F'  # Membaca EPC
# read EPC
readTagMem = '12 FF 02 02 11 22 33 44 01 00 04 00 00 00 00 00 02'
# change EPC
writeEpc = '0F 03 04 03 00 00 00 00 11 22 33 44 55 66'
# set data
setAddress = '05 03 24 00'


def crc(cmd):
    cmd = bytes.fromhex(cmd)
    uiCrcValue = PRESET_Value
    for x in range((len(cmd))):
        uiCrcValue = uiCrcValue ^ cmd[x]
        for y in range(8):
            if (uiCrcValue & amp; 0x0001):
                uiCrcValue = (uiCrcValue >> 1) ^ POLYNOMIAL
            else:
                uiCrcValue = uiCrcValue >> 1
    crc_H = (uiCrcValue >> 8) & amp
    0xFF
    crc_L = uiCrcValue & amp
    0xFF
    cmd = cmd + bytes([crc_L])
    cmd = cmd + bytes([crc_H])
    return cmd


def send_cmd(cmd):
    data = crc(cmd)
    print(data)
    test_serial.write(data)
    response = test_serial.read(512)
    response_hex = response.hex().upper()
    hex_list = [response_hex[i:i + 2] for i in range(0, len(response_hex), 2)]
    hex_space = ' '.join(hex_list)


send_cmd(INVENTORY1)
