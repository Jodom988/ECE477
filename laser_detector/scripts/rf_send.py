import pigpio
import time
import struct

from nrf24 import *

pi = pigpio.pi("127.0.0.1", 8888)

if not pi.connected:
	print("Couldn't connect to Raspberry Pi daemon, exiting...")
	exit()


USB_ADDR = b'\xAA\x44\x33\x22\x11'
LASER_ADDR = b'\x44\x44\x44\x44\x44'
SELF_ADDR = b'\x99\x88\x77\x66\x55'


nrf = NRF24(pi, ce=25, payload_size=5, channel=120, data_rate=RF24_DATA_RATE.RATE_250KBPS, pa_level=RF24_PA.MAX)

nrf.set_address_bytes(len(LASER_ADDR))
nrf.set_retransmission(15, 15)

nrf.open_reading_pipe(RF24_RX_ADDR.P4,LASER_ADDR)
nrf.open_reading_pipe(RF24_RX_ADDR.P5,USB_ADDR)
nrf.open_writing_pipe(LASER_ADDR)
nrf.open_writing_pipe(USB_ADDR)
nrf.open_writing_pipe(LASER_ADDR)


nrf._nrf_write_reg(NRF24.DYNPD, 0x3F)
nrf._nrf_write_reg(NRF24.FEATURE, 0x40)
print("About to send:")
nrf.show_registers()

payload = b'From Josh\x00'

i = 0

while (True):
	nrf.reset_packages_lost()
	nrf.send(payload)

	time.sleep(1)
	if nrf.get_packages_lost() == 1:
		print("1 NOT RECEIVED " + str(i))
	else:
		print("Received! " + str(i))

	print("Lost Packets: %d, Retries: %d" % (nrf.get_packages_lost(), nrf.get_retries()))
	#nrf.show_registers()

	i+=1

	time.sleep(1)

