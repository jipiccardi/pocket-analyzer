TEXT_INIT = chr(2)
TEXT_END = chr(3)

print(TEXT_END)
print(TEXT_INIT)
# from serial.tools import list_ports
# import serial
# import time
# # available_ports = list_ports.comports()
# # for p in available_ports:
# #     print(p)
#
# port = "COM4"
# try:
#     ser = serial.Serial(port, 115200, timeout=1)
# except Exception as e:
#     raise e
#
# readOut = 0
# print("Starting up")
# connected = False
# commandToSend = "Calibrate"
#
# while True:
#     try:
#         ser.write(commandToSend.encode())
#     except Exception as e:
#         ser.flush()
#         raise e
#     try:
#         time.sleep(1)
#         res = ser.readline()
#         print("echo "+str(res))
#
#     except Exception as e:
#         ser.flush()
#         raise e
#
#     ser.flush()
#     time.sleep(2)