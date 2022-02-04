import socket
import time
##import serial
##
##test_serial = serial.Serial('COM6', 57600, timeout=0.1)


RFID_Reader = "192.168.0.190"     #ip rfid reader
port_RFID_Reader = 6000           #port rfid reader


EPC = "04 00 01"        #EPC 12 byte - (24 hex)



MasterEPC = ["E2806894000050131FD22054",
                "E28068940000400B9693D200",
                "E2806894000040131FD22055",
                 "E20000203413015306107BDC"]

maxNoDetect = 3

print("Master EPC:")
countNoDetect = []
for me in MasterEPC:
    print(me)
    countNoDetect.append(0)
    




#crc
PRESET_Value = 0xFFFF
POLYNOMIAL = 0x8408

def crc(cmd):
    cmd = bytes.fromhex(cmd)
    uiCrcValue = PRESET_Value
    for x in range((len(cmd))):
        uiCrcValue = uiCrcValue ^ cmd[x]
        for y in range(8):
            if (uiCrcValue & 0x0001):
                uiCrcValue = (uiCrcValue >> 1) ^ POLYNOMIAL
            else:
                uiCrcValue = uiCrcValue >> 1
    crc_H = (uiCrcValue >> 8) & 0xFF
    crc_L = uiCrcValue & 0xFF
    #print(crc_H)
    #print(crc_L)
    cmd = cmd + bytes([crc_L])
    cmd = cmd + bytes([crc_H])
    return cmd


def send_cmd(cmd):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((RFID_Reader, port_RFID_Reader))
    message = crc(cmd)
    s.sendall(message)
    data = s.recv(1280)
    response_hex = data.hex().upper()
    hex_list = [response_hex[i:i + 2] for i in range(0, len(response_hex), 2)]
    hex_space = ' '.join(hex_list)
    #print(hex_space)
    s.close()
    return data


def send_cmd_serial(cmd):
    message = crc(cmd)
    test_serial.write(message)
    data = test_serial.read(1280)
    response_hex = data.hex().upper()
    hex_list = [response_hex[i:i + 2] for i in range(0, len(response_hex), 2)]
    hex_space = ' '.join(hex_list)
    print(hex_space)
    return data


print("Starting system")
print()
print()
print()

while True:
    try:
        HEX_data = send_cmd(EPC)   #send_cmd_serial(EPC) #untuk Serial
        #print(HEX_data)
        header = HEX_data[0]+1
        #print(header)
        if header > 15:         #minimum ada data 15 digit ( header 6 + 9 data epc 8byte)
            qty_data = HEX_data[4]  # banyaknya data ada di array ke 4 response
            #print(qty_data)
            data_RFID = []
            if qty_data > 0 and qty_data < 242:   #242 = F2 response from reader if no tag
                flag = 0
                incr = 0                                              
                HEX_data = HEX_data[5:(header-2)]   #remove header and CRC (-2 CRC 2byte)
                #print(HEX_data.hex().upper())   #original data + length without header
                
                for x in range(qty_data):
                    #print(x)
                    flag = flag + 1
                    incr = incr + 1
                    len_data_UIDx = HEX_data[(flag-1):flag]
                    len_data_UID = int.from_bytes(len_data_UIDx, byteorder='big', signed=False)
                    #print(len_data_UID)
                    data_to_save = HEX_data[flag:incr*len_data_UID+incr].hex().upper()
                    if len(data_to_save) == (len_data_UID*2):
                        data_RFID.append(data_to_save)
                    flag = flag + len_data_UID
            else:
                print("tidak ada data")

            #print(len(data_RFID))
            print()
            #print(data_RFID)
            print()
            
            index = 0
            for m in MasterEPC:
                sign = 0
                for r in data_RFID:
                    #print(r)
                    if r == m:
                        sign = sign + 1
                        
                if sign == 0:
                    print(m+" Tidak terdeteksi")
                    countNoDetect[index] = countNoDetect[index] + 1
                else:
                    print(m+" OK")
                    countNoDetect[index] = 0
                index = index+1
                
            print()
            
        else:
            print("tag tidak terbaca")
            index = 0
            for cnd in countNoDetect:
                countNoDetect[index] = countNoDetect[index] + 1
                index = index + 1
            print()
            print()

        print(countNoDetect)

        index = 0
        for cnd in countNoDetect:
            if cnd > maxNoDetect:
                print("Alarm Tag EPC -------------------------------------- : "+MasterEPC[index])
                GPIO.output(2,)
            index = index + 1

        #time.sleep(1.5)   # atur delay pembacaan
    except Exception as e:
        print(e)
